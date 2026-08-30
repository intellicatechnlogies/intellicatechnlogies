from Api.models import apiUser
from rest_framework.response import Response
from django.views.decorators.csrf           import csrf_exempt
from rest_framework.status   import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS,HTTP_400_BAD_REQUEST,HTTP_200_OK,HTTP_503_SERVICE_UNAVAILABLE
from rest_framework.decorators import api_view

@api_view(["POST","GET"])
@csrf_exempt
def data_insert(request):
    print("hiiiiiiiiiiiiiiiiiii")
    apiUser.objects.bulk_create([
    apiUser(api_key="KEY001", app_id="APP001", client="ClientA", platform="Linux"),
    apiUser(api_key="KEY002", app_id="APP002", client="ClientB", platform="Windows"),
    apiUser(api_key="KEY003", app_id="APP003", client="ClientC", platform="MacOS"),
    ])
    response_model={}
    print("hellooo")

    response_model["services"]=['KYC','IDR','Cface']
    return Response(data=response_model, status=HTTP_200_OK)