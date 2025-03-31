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
from json                                   import dumps as dump_as_JSON
from munch                                  import Munch
from django.views.decorators.csrf           import csrf_exempt
from rest_framework.decorators              import api_view
from models                                 import ServiceResult
from rest_framework.response                import Response
from rest_framework.status                  import HTTP_200_OK


@api_view(["GET","OPTIONS"])
@validate_credential
@csrf_exempt
def get_request_list(request):
    login_id = request.data.get('login_id')
    sr_result = list(ServiceResult.objects.filter(login_id=login_id).values_list('request_id',flat=True))
    
    if sr_result:
        response_status=HTTP_200_OK
        return Response(data={"login_id":login_id,"request_list": sr_result}, status=response_status)
 
    return Response(data={"login_id":login_id,"request_list": []}, status=response_status)
