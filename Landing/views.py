from django.shortcuts import render
from django.views.decorators.cache import never_cache
from login.views import create_login_captcha

# Create your views here.

@never_cache
def landing(request):
    return render(
        request,
        'index.html',
        {"captcha_question": create_login_captcha(request)},
    )