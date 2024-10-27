from django.shortcuts import render
#from Services.PAN import get_Pan_result
from datetime                               import datetime as dt
from django.http                            import HttpResponseRedirect, JsonResponse
from django.shortcuts                       import render
from django.views.decorators.cache          import never_cache
from django.views.decorators.http           import require_http_methods
from pytz                                   import timezone
from random                                 import getrandbits
from IntellicaTechnologies.decorators       import validate_credential
import requests
from rest_framework.response import Response
from rest_framework.status   import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS,HTTP_400_BAD_REQUEST,HTTP_200_OK,HTTP_503_SERVICE_UNAVAILABLE
from IntellicaTechnologies.regexValidators  import RegexPan_number,RegexMobile_number,RegexValidateDL, RegexEpic_number, RegexEmail_id, Regex_gst,RegexCylinder_number,RegexEbill_number,RegexService_provider_number,RegexMobile_number,RegexFssai_Number,RegexMsme_number,RegexRC_number,RegexAadhaar_number,RegexPan_number_Person,RegexPan_number_Person
import re
import imghdr
from json                                   import dumps as dump_as_JSON
from munch                                  import Munch
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view


@api_view(["POST","OPTIONS"])
@validate_credential
@csrf_exempt
def login(request):
        API_KEY = request.META.get("HTTP_API_KEY")
        API_KEY = request.META.get("HTTP_APP_ID")
        request_timestamp = dt.now(timezone("Asia/Kolkata")).__str__()
        #secret_id         = token_urlsafe(16)
        secret_id          = ""
        #transaction_id    = sha256(secret_id.encode()).hexdigest()
        transaction_id     =""
        response_model    = {}

        #client_name       = api_user.objects.get_client_name(API_KEY=API_KEY,APP_ID=APP_ID)
        client_name        =""
        # if login=='1234567':
        #     if password=='2345':
        #         response_model["services"]=['KYC','IDR']
        #         response_status=HTTP_200_OK
        #     else:
        #         response_model["password"]='Incorrect Password'
        #         response_status=HTTP_401_UNAUTHORIZED
        # elif login=='12345678':
        #     if password=='23456':
        #         response_model["services"]=['KYC','IDR','Cface']
        #         response_status=HTTP_200_OK
        #     else:
        #         response_model["password"]='Incorrect Password'
        #         response_status=HTTP_401_UNAUTHORIZED
        # else:
        #     response_model["login"]="Incorrect login id"
        #     response_status=HTTP_401_UNAUTHORIZED

        application_data  = request.data
        login_id=''
        pwd=''
        if 'data' in application_data.keys():
             login_id=application_data['data']["userid"] if 'userid' in application_data['data'].keys() else ''
             pwd=application_data['data']["password"] if 'password' in application_data['data'].keys() else ''
        else:
            login_id=application_data["userid"] if 'userid' in application_data.keys() else ''
            pwd=application_data['password']  if 'password' in application_data.keys() else ''

        if login_id=='1234567' and pwd=='234567':
            response_model["services"]=['KYC','IDR','Cface']
            response_status=HTTP_200_OK
        else:
            response_model["userid"]="Incorrect userid/password"
            response_status=HTTP_401_UNAUTHORIZED

        #data = {"message": "Success"}
        return Response(data=response_model, status=response_status)
        #return Response(data)

