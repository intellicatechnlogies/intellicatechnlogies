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
from rest_framework.response                import Response
from rest_framework.status                  import HTTP_200_OK
from Services.models                        import service_result


@api_view(["GET","OPTIONS","POST"])
@validate_credential
@csrf_exempt
def get_request_list(request):
    login_id = request.data.get('login_id')
    sr_result=service_result.objects.filter(login_id=login_id).order_by('-timestamp').values("Application_number","State","request_id","service_name","billable","timestamp")
    return Response(data=sr_result, status=HTTP_200_OK)
