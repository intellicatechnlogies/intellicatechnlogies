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
from django.views.decorators.csrf           import csrf_exempt
from rest_framework.decorators              import api_view
from login.models                           import users


def loginValidate(login_id,pwd):
     if users.objects.filter(login_id=login_id):
          if users.objects.filter(login_id=login_id,password=pwd):
               return True,"Success"
          else:
               return False,"Password is incorrect"
     else:
          return False, "Incorrect User id"

@api_view(["POST","OPTIONS"])
@validate_credential
@csrf_exempt
def login(request):
        #request_timestamp = dt.now(timezone("Asia/Kolkata")).__str__()
        response_model    = {}
        application_data  = request.data
        login_id=''
        pwd=''
        if 'data' in application_data.keys():
             login_id=application_data['data']["userid"] if 'userid' in application_data['data'].keys() else ''
             pwd=application_data['data']["password"] if 'password' in application_data['data'].keys() else ''
        else:
            login_id=application_data["userid"] if 'userid' in application_data.keys() else ''
            pwd=application_data['password']  if 'password' in application_data.keys() else ''

        #Validating credentials    
        login,message=loginValidate(login_id,pwd)
        if login:
             response_model["services"]=['KYC','IDR','Cface']
             response_status=HTTP_200_OK
        else:
             response_model["userid"]=message
             response_status=HTTP_401_UNAUTHORIZED
             
        return Response(data=response_model, status=response_status)
        

