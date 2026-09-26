from django.http             import HttpResponseRedirect
from django.shortcuts        import render
from functools               import partial, wraps
from threading               import Thread
from rest_framework.response import Response
from rest_framework.status   import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS
from Api.models              import apiUser
from login.views             import require_login


def validate_credential(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Browser users authenticate with their Django session; API clients
        # continue to authenticate with their API key and application ID.
        session_user = require_login(request)
        if session_user:
            request.login_user = session_user
            return view_func(request, *args, **kwargs)

        API_KEY = request.META.get("HTTP_API_KEY")
        APP_ID  = request.META.get("HTTP_APP_ID")
        response_model = {}
        if not API_KEY or not APP_ID:
            response_model["response_code"], response_model["response_message"], response_status = "401", "Bad credentials parameter", HTTP_401_UNAUTHORIZED
            return Response(data=response_model, status=response_status)
        else:
            #validate_credentials = api_user.objects.validate_credentials(API_KEY=API_KEY, APP_ID=APP_ID)

            #validate_credentials=True if API_KEY=='abcd' and APP_ID=='cdef' else False
            validate_credentials=apiUser.objects.validate_credentials(API_KEY=API_KEY, APP_ID=APP_ID)
            if not validate_credentials:
                response_model["response_code"], response_model["response_message"], response_status = "403", "Bad credentials provided", HTTP_403_FORBIDDEN
                return Response(data=response_model, status=response_status)
            else:
                #usage_quouta = api_user.objects.check_test_credit(API_KEY=API_KEY,APP_ID=APP_ID)
                usage_quouta=True
                if not usage_quouta:
                    response_model["response_code"], response_model["response_message"], response_status = "429", "Limit exceeded", HTTP_429_TOO_MANY_REQUESTS 
                    return Response(data=response_model, status=response_status)
                else:
                    return view_func(request, *args, **kwargs)
    return wrapper


def login_required(function):
    """Require an interactive user session for internal web-only views."""
    @wraps(function)
    def wrapped(request, *args, **kwargs):
        if not require_login(request):
            return Response(
                data={
                    "response_code": "401",
                    "response_message": "Login required",
                },
                status=HTTP_401_UNAUTHORIZED,
            )
        return function(request, *args, **kwargs)

    return wrapped