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
from Services.AWS                 import getCompareFaces,getFaceAnalysis,upload_Image_to_s3,download_json_from_S3,upload_JSON_to_s3
from uuid                         import uuid1
from Api.apiTransaction           import apiTransaction
from Services.TransactionLog      import TransactionLog



@api_view(["POST"])
@validate_credential
@csrf_exempt
def compareFace(request):
    API_KEY = request.META.get("HTTP_API_KEY")

    request_timestamp = dt.now(timezone("Asia/Kolkata")).__str__()
    timestamp=int(dt.timestamp(
        dt.now(timezone("Asia/Kolkata")))*1000000)
    
    transaction_id     =str(uuid1(getrandbits(32)))
    response_model    = {}
    application_data  = request.data
    imageid={}
    userid=application_data['userId'] if 'userId' in application_data.keys() else ""
    for keys,data in application_data.items():
       if keys!='userId':
        imageid[keys]=upload_Image_to_s3(data)

    # Check the request data is correct or not ...
    result={}
    if len(application_data.keys())<2:
        response_code, response_message, response_status = "102", "Minimum two image are required", HTTP_400_BAD_REQUEST
        billable,result = False, None
    else:
        try:
             cface_overview,cface_result = getCompareFaces(application_data,service='Cface',transaction=transaction_id,api_mode=False,service_type='')
             result["cf_result"]      = cface_result
             result["cf_overview"]    = cface_overview
             response_status          = HTTP_200_OK
             billable                 = "True"    
             response_code            ="101"  
             response_message         ="Success"         
        except Exception as ex:
            print(ex)
            #print_debug_msg(ex)
            billable, response_code, response_message, response_status, result = False, "503", "Service unavialable", HTTP_503_SERVICE_UNAVAILABLE, None
    apiTransaction.transactionCreated(API_KEY,transaction_id,timestamp,'Cface')
    response_model["transaction_id"]      = transaction_id
    response_model["success"]             = billable == "True"
    response_model["response_code"]       = response_code
    response_model["response_message"]    = response_message
    response_model["result"]              = result
    response_model['imageid']             = imageid
    response_model["resquest_timestamp"]  = request_timestamp
    file_name=upload_JSON_to_s3(response_model,transaction_id)
    TransactionLog.createServiceResult(int("111111"),transaction_id,timestamp,"Cface",True)
    return Response(data=response_model, status=response_status)


@api_view(["POST"])
@validate_credential
@csrf_exempt
def faceAnalysis(request):
    API_KEY = request.META.get("HTTP_API_KEY")

    request_timestamp = dt.now(timezone("Asia/Kolkata")).__str__()
    timestamp=int(dt.timestamp(
        dt.now(timezone("Asia/Kolkata")))*1000000)
    transaction_id     =str(uuid1(getrandbits(32)))
   
    response_model    = {}
    application_data  = request.data
    # Check the request data is correct or not ...
    result={}
    if len(application_data.keys())<1:
        response_code, response_message, response_status = "102", "Minimum one image is required", HTTP_400_BAD_REQUEST
        billable,result = False, None
    else:
        # try:
             cface_result = getFaceAnalysis(application_data["image"])
             result['cface']=cface_result
             #result["cf_overview"]    = cface_overview
             response_status          = HTTP_200_OK
             billable                 = "True"    
             response_code            ="101"  
             response_message         ="Success"         
        # except Exception as ex:
        #     #print_debug_msg(ex)
        #     billable, response_code, response_message, response_status, result = False, "503", "Service unavialable", HTTP_503_SERVICE_UNAVAILABLE, None
        
    response_model["transaction_id"]      = transaction_id
    response_model["success"]             = billable == "True"
    response_model["response_code"]       = response_code
    response_model["response_message"]    = response_message
    response_model["result"]              = result
    response_model["resquest_timestamp"]  = request_timestamp
    apiTransaction.transactionCreated(API_KEY,transaction_id,timestamp,'Cface')
    return Response(data=response_model, status=response_status)


@api_view(["POST"])
@validate_credential
@csrf_exempt
def downloadImage(request):
    API_KEY = request.META.get("HTTP_API_KEY")
    APP_ID  = request.META.get("HTTP_APP_ID")

    request_timestamp = dt.now(timezone("Asia/Kolkata")).__str__()
    #secret_id         = token_urlsafe(16)
    secret_id          = ""
    #transaction_id    = sha256(secret_id.encode()).hexdigest()
    transaction_id     =""
    response_model    = {}
    response_code     ="101"
    response_message  ="Success"
    response_status             =HTTP_200_OK
    img="00500"
    
    #client_name       = api_user.objects.get_client_name(API_KEY=API_KEY,APP_ID=APP_ID)
    client_name        =""
    application_data  = request.data
    if 'imagepath' in application_data.keys():
        print("downloadImage..............................................................",application_data['imagepath'])
        img=download_json_from_S3(application_data['imagepath'])
        if img[1]==500:
         response_code="102"
         response_message="Incorrect imageid"
         response_status          = HTTP_400_BAD_REQUEST
    else:
         response_code="102"
         response_message="imagepath is missing"
         response_status          = HTTP_400_BAD_REQUEST
    
    response_model["transaction_id"]      = transaction_id
    response_model["success"]             = "True"
    response_model["response_code"]       = response_code
    response_model["response_message"]    = response_message
    response_model["result"]              = img[1]
    response_model["resquest_timestamp"]  = request_timestamp
    response_model["response_timestamp"]  = dt.now(timezone("Asia/Kolkata")).__str__()

    return Response(data=response_model, status=response_status)

@api_view(["POST"])
@validate_credential
@csrf_exempt
def downloadResult(request):
    API_KEY = request.META.get("HTTP_API_KEY")
    APP_ID  = request.META.get("HTTP_APP_ID")

    request_timestamp = dt.now(timezone("Asia/Kolkata")).__str__()
    #secret_id         = token_urlsafe(16)
    secret_id          = ""
    #transaction_id    = sha256(secret_id.encode()).hexdigest()
    transaction_id     =""
    response_model    = {}
    response_code     ="101"
    response_message  ="Success"
    response_status             =HTTP_200_OK
    img="00500"
    
    #client_name       = api_user.objects.get_client_name(API_KEY=API_KEY,APP_ID=APP_ID)
    client_name        =""
    application_data  = request.data
    if 'trxid' in application_data.keys():
        trx_id=application_data['trxid']
        filename="intellica-datastore/"+trx_id+".json"
        print("downloadResult..............................................................",filename)
        img=download_json_from_S3(filename)
        if img[1]==500:
         response_code="102"
         response_message="Incorrect imageid"
         response_status          = HTTP_400_BAD_REQUEST
    else:
         response_code="102"
         response_message="imagepath is missing"
         response_status          = HTTP_400_BAD_REQUEST
    
    response_model["transaction_id"]      = transaction_id
    response_model["success"]             = "True"
    response_model["response_code"]       = response_code
    response_model["response_message"]    = response_message
    response_model["result"]              = img[1]
    response_model["resquest_timestamp"]  = request_timestamp
    response_model["response_timestamp"]  = dt.now(timezone("Asia/Kolkata")).__str__()

    return Response(data=response_model, status=response_status)

    

