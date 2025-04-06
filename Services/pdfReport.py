
from django.template.loader           import get_template
from django.http                      import HttpResponse
try:
    from weasyprint import HTML
except Exception as ex:
    print(f"Error, Pdf reports are not available! Reason being {ex}")

def cface_report(request, verification_request_id):

    # images      = result_json["result"]["images"]
    # img_dict    = {
    #     img_id: get_img_base64(image_id=img_filename)
    #     for img_id, img_filename in images.items()
    # }
    # result_json["image_data"] = img_dict   
    
    # update_erpv_request = erpv_request.objects.get(verification_id=verification_request_id)
    # update_erpv_request.download_result = True
    # update_erpv_request.save()

    template = get_template("ERPV/report.html")
    response =  HttpResponse(HTML(string=template.render(result_json)).write_pdf(), content_type='application/pdf/force-download')
    response['Content-Disposition'] = f'attachment; filename="E-RPV_Result_{verification_request_id}.pdf"'
    return response