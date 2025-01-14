from django.http             import HttpResponseRedirect
from django.shortcuts        import render
from functools               import partial, wraps
from threading               import Thread
from rest_framework.response import Response
from rest_framework.status   import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS
from Api.models              import apiUser


def validate_credential(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
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
	"""
	@login_required\
	def function_name(request):
		#do_stuff
	"""
	# def wrapped(request, *args, **kwargs):
	# 	# # If Unique ID and Login ID are authenticated...
	# 	# if "login_id" in request.session.keys() and users.objects.is_session_active(LOGIN_ID=request.session["login_id"]):
	# 	# 	if "logged_in" in request.session.keys() and request.session["logged_in"]=="T":
	# 	# 		return function(request, *args, **kwargs)
	# 	# return HttpResponseRedirect('/login')

    # wrapped.__doc__  = function.__doc__
	# wrapped.__name__ = function.__name__
	# return wrapped