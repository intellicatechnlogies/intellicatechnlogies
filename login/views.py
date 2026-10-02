import secrets

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.crypto import constant_time_compare
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from login.authentication import get_user_for_login, verify_user_password
from login.models import users

# Create your views here.

def create_login_captcha(request, *, exclude_answer=None):
    """Create a simple, accessible CAPTCHA challenge bound to this session."""
    while True:
        left = secrets.randbelow(8) + 2
        right = secrets.randbelow(8) + 2
        answer = str(left + right)
        if answer != exclude_answer:
            break
    request.session["login_captcha_answer"] = answer
    return f"{left} + {right}"


def _render_login(request, *, error=None, status=200):
    return render(
        request,
        "login.html",
        {
            "error": error,
            "captcha_question": create_login_captcha(request),
        },
        status=status,
    )


@require_POST
def refresh_login_captcha(request):
    return JsonResponse({"captcha_question": create_login_captcha(request)})

@never_cache
def LoginUser(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if request.method == "POST":
        expected_captcha = request.session.pop("login_captcha_answer", "")
        submitted_captcha = request.POST.get("captcha_answer", "").strip()
        if not expected_captcha or not submitted_captcha or not constant_time_compare(
            expected_captcha, submitted_captcha
        ):
            error = "Please solve the CAPTCHA correctly."
            captcha_question = create_login_captcha(
                request, exclude_answer=expected_captcha
            )
            if is_ajax:
                return JsonResponse(
                    {
                        "ok": False,
                        "error": error,
                        "captcha_question": captcha_question,
                    },
                    status=400,
                )
            return render(
                request,
                "login.html",
                {"error": error, "captcha_question": captcha_question},
                status=400,
            )

        identity = request.POST.get("loginid", "")
        password = request.POST.get("psw", "")
        user = get_user_for_login(identity)

        if user and verify_user_password(user, password):
            request.session.cycle_key()
            request.session["login_id"] = str(user.login_id)
            request.session["user_name"] = user.user_name
            request.session.pop("login_captcha_answer", None)
            if is_ajax:
                return JsonResponse({"ok": True, "redirect_url": "/home"})
            return redirect("/home")

        error = "Invalid username/login ID or password."
        captcha_question = create_login_captcha(
            request, exclude_answer=expected_captcha
        )
        if is_ajax:
            return JsonResponse(
                {
                    "ok": False,
                    "error": error,
                    "captcha_question": captcha_question,
                },
                status=401,
            )
        return render(
            request,
            "login.html",
            {"error": error, "captcha_question": captcha_question},
            status=401,
        )

    return _render_login(request)


@require_POST
def LogoutUser(request):
    request.session.flush()
    return redirect("/login")


def require_login(request):
    login_id = request.session.get("login_id")
    if not login_id:
        return None

    user = users.objects.filter(login_id=login_id, login_active=True).first()
    if user:
        return user

    request.session.flush()
    return None

