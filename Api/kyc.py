from django.shortcuts import render
#from Services.PAN import get_Pan_result
from datetime                               import datetime as dt
from django.http                            import HttpResponseRedirect, JsonResponse
from django.shortcuts                       import render
from django.views.decorators.cache          import never_cache
from django.views.decorators.http           import require_http_methods
from pytz                                   import timezone
from random                                 import getrandbits
import requests
from rest_framework.response import Response
from rest_framework.status   import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS,HTTP_400_BAD_REQUEST,HTTP_200_OK,HTTP_503_SERVICE_UNAVAILABLE
from IntellicaTechnologies.regexValidators  import RegexPan_number,RegexMobile_number,RegexValidateDL, RegexEpic_number, RegexEmail_id, Regex_gst,RegexCylinder_number,RegexEbill_number,RegexService_provider_number,RegexMobile_number,RegexFssai_Number,RegexMsme_number,RegexRC_number,RegexAadhaar_number,RegexPan_number_Person,RegexPan_number_Person
import re
import imghdr
from json                                   import dumps as dump_as_JSON
from munch                                  import Munch
from rest_framework.decorators import api_view
from IntellicaTechnologies.decorators      import validate_credential
from django.views.decorators.csrf import csrf_exempt
from Services.PAN                 import panCall
from Services.nameMatch           import nameMatch
from Services.Distance            import getdistance


@api_view(["POST"])
@validate_credential
@csrf_exempt
def pan_kyc(request):
    API_KEY = request.META.get("HTTP_API_KEY")
    APP_ID  = request.META.get("HTTP_APP_ID")

    request_timestamp = dt.now(timezone("Asia/Kolkata")).__str__()
    #secret_id         = token_urlsafe(16)
    secret_id          = ""
    #transaction_id    = sha256(secret_id.encode()).hexdigest()
    transaction_id     =""
    response_model    = {}
    application_data  = request.data
    # Check the request data is correct or not ...
    if "pan_number" not in application_data.keys():
        response_code, response_message, response_status = "102", "Invalid combination of input", HTTP_400_BAD_REQUEST
        billable,result = False, None
    # Check the format of the PAN Number ...
    elif not RegexPan_number(application_data["pan_number"]):
        result, billable, response_code, response_message, response_status = None, False, "102", "Invalid format of the PAN Number.", HTTP_400_BAD_REQUEST
    # If everything seems OK then we can hit the source API for the result data...
    else:
        try:
            input_params     = Munch()
            input_params.pan = application_data["pan_number"]
            pan_result, billable, response_code, response_message, _ = panCall(application_data=input_params, api_mode=True)
            if response_code in ['101', '103']:
                response_status = HTTP_200_OK
                #api_user.objects.usage_quouta_decrement(API_KEY=API_KEY,APP_ID=APP_ID)
            elif response_code in ['102', '104', '105']:
                response_status = HTTP_400_BAD_REQUEST
            else:
                response_status = HTTP_503_SERVICE_UNAVAILABLE
            result = {key : value for key,value in pan_result.items() if key not in ["pan_no","response_code","date_time"]}                
        except Exception as ex:
            #print_debug_msg(ex)
            billable, response_code, response_message, response_status, result = False, "503", "Service unavialable", HTTP_503_SERVICE_UNAVAILABLE, None
        
    response_model["transaction_id"]      = transaction_id
    response_model["success"]             = billable == "True"
    response_model["response_code"]       = response_code
    response_model["response_message"]    = response_message
    response_model["result"]              = result
    response_model["resquest_timestamp"]  = request_timestamp
    response_model["response_timestamp"]  = dt.now(timezone("Asia/Kolkata")).__str__()
    #cl_trx_log.objects.create_log(client_name=client_name, api_key=API_KEY, service="API", api_name="PAN", billable=billable, response_code=response_code, response_message=response_message, trx_id=transaction_id)
    
    return Response(data=response_model, status=response_status)

@api_view(["POST"])
@validate_credential
@csrf_exempt
def name_match(request):
    API_KEY = request.META.get("HTTP_API_KEY")
    APP_ID  = request.META.get("HTTP_APP_ID")

    request_timestamp = dt.now(timezone("Asia/Kolkata")).__str__()
    #secret_id         = token_urlsafe(16)
    secret_id          = ""
    #transaction_id    = sha256(secret_id.encode()).hexdigest()
    transaction_id     =""
    response_model    = {}

    application_data  = request.data
    # Check the request data is correct or not ...
    if "name1" not in application_data.keys() or "name2" not in application_data.keys():
        response_code, response_message, response_status = "102", "Invalid combination of input", HTTP_400_BAD_REQUEST
        billable,result = False, None
    else:
        try:
            result=Munch()
            input_params     = Munch()
            input_params.name1 = application_data["name1"]
            input_params.name2 = application_data["name2"]
            result.score, billable, response_code, response_message = nameMatch(input_params.name1,input_params.name2)
            if response_code in ['101', '103']:
                response_status = HTTP_200_OK
                #api_user.objects.usage_quouta_decrement(API_KEY=API_KEY,APP_ID=APP_ID)
            elif response_code in ['102', '104', '105']:
                response_status = HTTP_400_BAD_REQUEST
            else:
                response_status = HTTP_503_SERVICE_UNAVAILABLE              
        except Exception as ex:
            #print_debug_msg(ex)
            billable, response_code, response_message, response_status, result = False, "503", "Service unavialable", HTTP_503_SERVICE_UNAVAILABLE, None
        
    response_model["transaction_id"]      = transaction_id
    response_model["success"]             = billable == "True"
    response_model["response_code"]       = response_code
    response_model["response_message"]    = response_message
    response_model["result"]              = result
    response_model["resquest_timestamp"]  = request_timestamp
    response_model["response_timestamp"]  = dt.now(timezone("Asia/Kolkata")).__str__()
    #cl_trx_log.objects.create_log(client_name=client_name, api_key=API_KEY, service="API", api_name="PAN", billable=billable, response_code=response_code, response_message=response_message, trx_id=transaction_id)
    
    return Response(data=response_model, status=response_status)


@api_view(["POST"])
@validate_credential
@csrf_exempt
def getDistanceResult(request):
    request_timestamp = dt.now(timezone("Asia/Kolkata")).__str__()
    #secret_id         = token_urlsafe(16)
    secret_id          = ""
    #transaction_id    = sha256(secret_id.encode()).hexdigest()
    transaction_id     =""
    response_model    = {}
    
    #client_name       = api_user.objects.get_client_name(API_KEY=API_KEY,APP_ID=APP_ID)
    client_name        =""
    application_data  = request.data
    # Check the request data is correct or not ...
    if "address1" not in application_data.keys() or "address2" not in application_data.keys():
        response_code, response_message, response_status = "102", "Invalid combination of input", HTTP_400_BAD_REQUEST
        billable,result = False, None
    else:
        # try:
            result, billable, response_code, response_message = getdistance(application_data=application_data,api_mode=True)
            if response_code in ['101', '103']:
                response_status = HTTP_200_OK
                #api_user.objects.usage_quouta_decrement(API_KEY=API_KEY,APP_ID=APP_ID)
            elif response_code in ['102', '104', '105']:
                response_status = HTTP_400_BAD_REQUEST
            else:
                response_status = HTTP_503_SERVICE_UNAVAILABLE              
        # except Exception as ex:
        #     #print_debug_msg(ex)
        #     billable, response_code, response_message, response_status, result = False, "503", "Service unavialable", HTTP_503_SERVICE_UNAVAILABLE, None
        
    response_model["transaction_id"]      = transaction_id
    response_model["success"]             = billable == "True"
    response_model["response_code"]       = response_code
    response_model["response_message"]    = response_message
    response_model["result"]              = result
    response_model["resquest_timestamp"]  = request_timestamp
    response_model["response_timestamp"]  = dt.now(timezone("Asia/Kolkata")).__str__()
    #cl_trx_log.objects.create_log(client_name=client_name, api_key=API_KEY, service="API", api_name="PAN", billable=billable, response_code=response_code, response_message=response_message, trx_id=transaction_id)
    
    return Response(data=response_model, status=response_status)


