from django.shortcuts import render
#from Services.PAN import get_Pan_result
from datetime                               import datetime as dt
from zoneinfo                               import ZoneInfo
from base64                                 import b64decode
from binascii                               import Error as Base64DecodeError
from django.http                            import HttpResponseRedirect, JsonResponse
from django.shortcuts                       import render
from django.views.decorators.cache          import never_cache
from django.views.decorators.http           import require_http_methods
from random                                 import getrandbits
import requests
from rest_framework.response import Response
from rest_framework.status   import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS,HTTP_400_BAD_REQUEST,HTTP_200_OK,HTTP_503_SERVICE_UNAVAILABLE
from IntellicaTechnologies.regexValidators  import RegexPan_number,RegexMobile_number,RegexValidateDL, RegexEpic_number, RegexEmail_id, Regex_gst,RegexCylinder_number,RegexEbill_number,RegexService_provider_number,RegexMobile_number,RegexFssai_Number,RegexMsme_number,RegexRC_number,RegexAadhaar_number,RegexPan_number_Person,RegexPan_number_Person
import re
#import imghdr
from json                                   import dumps as dump_as_JSON
from munch                                  import Munch
from rest_framework.decorators import api_view
from IntellicaTechnologies.decorators      import validate_credential
from django.views.decorators.csrf import csrf_exempt
from Services.AWS                 import getCompareFaces,getFaceAnalysis,upload_Image_to_s3,download_json_from_S3,upload_JSON_to_s3
from uuid                         import uuid1
from Api.apiTransaction           import apiTransaction
from Services.TransactionLog      import TransactionLog
FACE_IMAGE_TYPES = (
    "PAN_INPUT",
    "AADHAAR_INPUT",
    "VOTER_INPUT",
    "DL_INPUT",
    "PASSPORT_INPUT",
)
LIVE_IMAGE_TYPE = "LIVE_INPUT"
MAX_FACE_IMAGES = 10
FACE_REQUEST_METADATA_FIELDS = {"application_number", "state", "product"}


def normalize_face_images(application_data):
    """Expand document image arrays and numbered fields into unique image keys."""
    images = {}
    unsupported = []
    for field_name, field_value in application_data.items():
        if field_name == "userId" or field_name in FACE_REQUEST_METADATA_FIELDS:
            continue

        base_type = next(
            (
                image_type
                for image_type in (*FACE_IMAGE_TYPES, LIVE_IMAGE_TYPE)
                if field_name == image_type
                or (
                    image_type != LIVE_IMAGE_TYPE
                    and field_name.startswith(f"{image_type}_")
                    and field_name[len(image_type) + 1 :].isdigit()
                    and int(field_name[len(image_type) + 1 :]) >= 1
                )
            ),
            None,
        )
        if base_type is None:
            unsupported.append(field_name)
            continue

        if base_type == LIVE_IMAGE_TYPE and isinstance(field_value, (list, tuple)):
            if len(field_value) != 1:
                return None, f"{LIVE_IMAGE_TYPE} must contain exactly one live image."
            field_value = field_value[0]

        values = field_value if isinstance(field_value, (list, tuple)) else [field_value]
        if not values:
            return None, f"{field_name} must contain at least one image."

        is_numbered_field = field_name != base_type
        for index, value in enumerate(values, start=1):
            if is_numbered_field:
                image_name = field_name if len(values) == 1 else f"{field_name}_{index}"
            elif index == 1:
                image_name = base_type
            else:
                image_name = f"{base_type}_{index}"
            if image_name in images:
                return None, f"Duplicate image field: {image_name}."
            images[image_name] = value

    if unsupported:
        return None, f"Unsupported image type supplied: {unsupported[0]}."
    return images, None





@api_view(["POST"])
@validate_credential
@csrf_exempt
def compareFace(request):
    API_KEY = request.META.get("HTTP_API_KEY")
    session_user = getattr(request, "login_user", None)
    if session_user:
        API_KEY = API_KEY or str(session_user.login_id)

    request_timestamp = dt.now(ZoneInfo("Asia/Kolkata")).__str__()
    timestamp=int(dt.timestamp(
        dt.now(ZoneInfo("Asia/Kolkata")))*1000000)
    
    transaction_id     =str(uuid1(getrandbits(32)))
    response_model    = {}
    application_data = request.data
    image_data, normalization_error = normalize_face_images(application_data)
    request_context = {
        "application_number": str(application_data.get("application_number") or transaction_id).strip()[:75],
        "state": str(application_data.get("state") or (session_user.state if session_user else "India")).strip()[:45],
        "product": str(application_data.get("product") or "Face Comparison").strip()[:75],
    }
    imageid = {}
    result = {}
    if normalization_error:
        response_code = "102"
        response_message = normalization_error
        response_status = HTTP_400_BAD_REQUEST
        billable = False
    elif LIVE_IMAGE_TYPE not in image_data or not any(
        image_name != LIVE_IMAGE_TYPE for image_name in image_data
    ):
        response_code = "102"
        response_message = "A live image and at least one document image are required."
        response_status = HTTP_400_BAD_REQUEST
        billable = False
    elif len(image_data) > MAX_FACE_IMAGES:
        response_code = "102"
        response_message = f"A maximum of {MAX_FACE_IMAGES} images, including the live image, can be compared at once."
        response_status = HTTP_400_BAD_REQUEST
        billable = False
    else:
        validation_error = None
        for image_name, encoded_image in image_data.items():
            if not isinstance(encoded_image, str) or not encoded_image:
                validation_error = f"{image_name} must contain a valid image."
                break
            if len(encoded_image) > 7_000_000:
                validation_error = f"{image_name} exceeds the 5 MB upload limit."
                break
            try:
                image_bytes = b64decode(encoded_image, validate=True)
            except (Base64DecodeError, ValueError):
                validation_error = f"{image_name} is not valid base64 image data."
                break
            if not image_bytes.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff")):
                validation_error = f"{image_name} must be a PNG or JPEG image."
                break

        if validation_error:
            response_code = "102"
            response_message = validation_error
            response_status = HTTP_400_BAD_REQUEST
            billable = False
        else:
            try:
                user_id = session_user.login_id if session_user else application_data.get("userId", 1111)
                comparison_data = dict(image_data)
                comparison_data["userId"] = user_id
                for image_name, encoded_image in image_data.items():
                    imageid[image_name] = upload_Image_to_s3(encoded_image)

                cface_overview, cface_result = getCompareFaces(
                    comparison_data,
                    service="Cface",
                    transaction=transaction_id,
                    api_mode=False,
                    service_type="",
                    request_context=request_context,
                )
                result["cf_result"] = cface_result
                result["cf_overview"] = cface_overview
                response_status = HTTP_200_OK
                billable = "True"
                response_code = "101"
                response_message = "Success"
            except Exception as ex:
                print(ex)
                billable, response_code, response_message, response_status, result = (
                    False,
                    "503",
                    "Face comparison service is unavailable.",
                    HTTP_503_SERVICE_UNAVAILABLE,
                    None,
                )

    if response_code == "101":
        apiTransaction.transactionCreated(API_KEY, transaction_id, timestamp, "Cface")
    response_model["transaction_id"]      = transaction_id
    response_model["success"]             = billable == "True"
    response_model["response_code"]       = response_code
    response_model["response_message"]    = response_message
    response_model["result"]              = result
    response_model['imageid']             = imageid
    response_model["report_metadata"]     = request_context
    response_model["resquest_timestamp"]  = request_timestamp
    if response_code == "101":
        result_login_id = session_user.login_id if session_user else int("111111")
        stored_response_model = dict(response_model)
        stored_response_model["login_id"] = result_login_id
        stored_response_model["report_metadata"] = request_context
        upload_JSON_to_s3(stored_response_model, transaction_id)
        TransactionLog.createServiceResult(
            result_login_id, transaction_id, timestamp, "Cface", True,
            application_no=request_context["application_number"],
            state=request_context["state"],
        )
    return Response(data=response_model, status=response_status)


@api_view(["POST"])
@validate_credential
@csrf_exempt
def faceAnalysis(request):
    API_KEY = request.META.get("HTTP_API_KEY")

    request_timestamp = dt.now(ZoneInfo("Asia/Kolkata")).__str__()
    timestamp=int(dt.timestamp(
        dt.now(ZoneInfo("Asia/Kolkata")))*1000000)
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

    request_timestamp = dt.now(ZoneInfo("Asia/Kolkata")).__str__()
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
    response_model["response_timestamp"]  = dt.now(ZoneInfo("Asia/Kolkata")).__str__()

    return Response(data=response_model, status=response_status)

@api_view(["POST"])
@validate_credential
@csrf_exempt
def downloadResult(request):
    API_KEY = request.META.get("HTTP_API_KEY")
    APP_ID  = request.META.get("HTTP_APP_ID")

    request_timestamp = dt.now(ZoneInfo("Asia/Kolkata")).__str__()
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
    response_model["response_timestamp"]  = dt.now(ZoneInfo("Asia/Kolkata")).__str__()

    return Response(data=response_model, status=response_status)

    

