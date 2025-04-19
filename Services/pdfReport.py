
from django.template.loader                 import get_template
from django.http                            import HttpResponse
from IntellicaTechnologies.decorators       import validate_credential
from json                                   import dumps as dump_as_JSON
from munch                                  import Munch
from django.views.decorators.csrf           import csrf_exempt
from rest_framework.decorators              import api_view
from rest_framework.response                import Response
from rest_framework.status                  import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS,HTTP_400_BAD_REQUEST,HTTP_200_OK,HTTP_503_SERVICE_UNAVAILABLE
from Services.AWS                           import getCompareFaces,getFaceAnalysis,upload_Image_to_s3,download_json_from_S3,upload_JSON_to_s3

try:
    from weasyprint import HTML
except Exception as ex:
    print(f"Error, Pdf reports are not available! Reason being {ex}")

def getResultWithImage(cface_result):
    for imageid,path in cface_result["imageid"].items():
        img=download_json_from_S3(path)
        if img[1]==500:
            break
        else:
           cface_result["imageid"][imageid]=img[1]["img"]
    return cface_result

# @api_view(["GET","OPTIONS","POST"])
# @validate_credential
# @csrf_exempt
def cface_report(request):
    response_code=500
    response_model=Munch()
    response_model.result=Munch()
    result_image={}
    transaction_id=""
    request_id = request.GET.get('trxid')
    print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii',request_id)
    if request_id:
        filename="intellica-datastore/"+request_id+".json"
        result=download_json_from_S3(filename)
        #print("result........................................",result)
        if result[1]==500:
         response_code="102"
         response_message="Incorrect imageid"
         response_status          = HTTP_400_BAD_REQUEST
        else:
            print('hi............................................................')
            response_code=101
            cface_result=result[1]
            print(cface_result)
            response_model.result=getResultWithImage(cface_result)
            response_status=HTTP_200_OK
            print('Exxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
            template = get_template("report.html")
            print("ressssssssssssssssssssssssssssssssssssssssssss")
            #response =  HttpResponse(HTML(string=template.render(result_image)).write_pdf(), content_type='application/pdf/force-download')
            response =  HttpResponse(HTML(string=template.render(response_model)).write_pdf(), content_type='application/pdf/force-download')
            print('CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCcc')
            response['Content-Disposition'] = f'attachment; filename="Cface_Result_{request_id}.pdf"'
            print('hoiiiiiiiiiiiiiiiiiiiiiiiiiiii')
            return response
    else:
         response_code="102"
         response_message="imagepath is missing"
         response_status          = HTTP_400_BAD_REQUEST
    
    response_model["transaction_id"]      = transaction_id
    response_model["success"]             = "True"
    response_model["response_code"]       = response_code
    #response_model["response_message"]    = response_message
    response_model["result"]              = result_image
    #response_model["resquest_timestamp"]  = request_timestamp
    #response_model["response_timestamp"]  = dt.now(timezone("Asia/Kolkata")).__str__()

    return Response(data=response_model, status=response_status)
