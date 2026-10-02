# from core.components.API.cloud_services.AWS import IMG2PNG
# from core.components.API.cloud_services.GCP import bytes_to_text
from base64                                 import b64encode, decodebytes
from datetime                               import datetime as dt
from io                                     import BytesIO
from json                                   import dumps as dump_as_JSON
from munch                                  import Munch
from pdf2image                              import convert_from_bytes
from requests                               import request as make_HTTP_request
from threading                              import Thread
# from dateutil.parser                        import parse as dateutil_parser
from Services.billings                      import billable_and_response_msg
# from TimbleGlanceWeb.utils.config           import Config
# from core.components.API.clients.MatchPercent import getMatchPercent
# from core.models                            import transactions_log
# from core.utils                             import print_debug_msg
# from .                                      import CKYC_verification
from Services.nameMatch import nameMatch

# config = Config()

# base_url = config.zoop_base_url["base_url"]

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    # try: 
    #     dateutil_parser(string, fuzzy=fuzzy)
    #     return True
    # except ValueError:
    #     return False

""" 
    ██████╗   █████╗  ███╗   ██╗
    ██╔══██╗ ██╔══██╗ ████╗  ██║
    ██████╔╝ ███████║ ██╔██╗ ██║
    ██╔═══╝  ██╔══██║ ██║╚██╗██║
    ██║      ██║  ██║ ██║ ╚████║
    ╚═╝      ╚═╝  ╚═╝ ╚═╝  ╚═══╝
"""

# def convert_pdfbase64_to_imagepdf(pdf_base64):
#     image  = convert_from_bytes(decodebytes(pdf_base64.encode()))[0]
#     imgArr = BytesIO()
#     image.save(imgArr, format='png')
#     return b64encode(imgArr.getvalue()).decode('ascii')

class Pan():
    def __init__(self, pan_no=""):
        Thread.__init__(self)
        self.__pan_no = pan_no
        # Result of the Pan
        self.__result_dict                        = Munch()
        self.__result_dict.response_code          = "500"
        self.__result_dict.pan_number             = ""
        self.__result_dict.pan_status             = ""
        self.__result_dict.pan_type               = ""
        self.__result_dict.pan_last_updated       = ""
        self.__result_dict.name_on_card           = ""
        self.__result_dict.first_name             = ""
        self.__result_dict.last_name              = ""
        self.__result_dict.aadhaar_seeding_status = ""
        self.__result_dict.pan_no                 = pan_no
        self.__response_metadata                  = Munch()
        self.get_Pan_result()

    def get_Pan_result(self):
        # try:
            #url = f"{base_url}/in/identity/pan/advance"

            # payload = dump_as_JSON({
            # "data": {
            #     "customer_pan_number": str(self.__pan_no),
            #     "consent": "Y",
            #     "consent_text": "I hear by declare my consent agreement for fetching my information via ZOOP API."
            # }
            # })
            # headers = {
            # 'api-key': config.zoop["api-key"],
            # 'app-id': config.zoop["app-id"],
            # 'Content-Type': 'application/json'
            # }


            #response = make_HTTP_request(method="POST",url=url,headers=headers,data=payload)
            response=Munch()
            response.status_code="200"
            #api_response = response.json()
            api_response=Munch()
            api_response.response_code="100"
            self.__response_metadata = {key : value for key,value in api_response.items() if key != "result"}
            if str(response.status_code) == "200":
                if str(api_response["response_code"]) == "100":
                    self.__result_dict.response_code = "101"
                    print('......................fgdffgfghg')
                    api_response_data = api_response["result"] if "result" in api_response.keys() else {}
                    print('......................fgdffgfghg1')
                    self.__result_dict.pan_number             = api_response_data["pan_number"] if ("pan_number" in api_response_data.keys() and api_response_data["pan_number"].strip() not in ["","NA"]) else "Data Not Available"
                    print('......................fgdffgfgh2')
                    self.__result_dict.pan_status             = api_response_data["pan_status"] if ("pan_status" in api_response_data.keys() and api_response_data["pan_status"].strip() not in ["", "NA"]) else "Data Not Available"
                    print('......................fgdffgfghg3')
                    self.__result_dict.pan_type               = api_response_data["pan_type"]   if ("pan_type" in api_response_data.keys() and api_response_data["pan_type"].strip() not in ["","NA"]) else "Data Not Available"
                    print('......................fgdffgfghg4')
                    self.__result_dict.pan_last_updated       = api_response_data["pan_last_updated"] if ("pan_last_updated" in api_response_data.keys() and api_response_data["pan_last_updated"].strip() not in ["", "NA"]) else "Data Not Available"
                    print('......................fgdffgfghg5')
                    self.__result_dict.name_on_card           = api_response_data["name_on_card"] if ("name_on_card" in api_response_data.keys() and api_response_data["name_on_card"].strip() not in ["", "NA"]) else "Data Not Available"
                    print('......................fgdffgfghg6')
                    self.__result_dict.user_title             = api_response_data["user_title"] if ("user_title" in api_response_data.keys() and api_response_data["user_title"].strip() not in ["","NA"]) else ""
                    print('......................fgdffgfghg7')
                    self.__result_dict.first_name             = api_response_data["user_first_name"] if ("user_first_name" in api_response_data.keys() and api_response_data["user_first_name"].strip() not in ["", "NA"]) else "Data Not Available"
                    print('......................fgdffgfghg8')
                    self.__result_dict.middle_name            = api_response_data["user_middle_name"] if ("user_middle_name" in api_response_data.keys() and api_response_data["user_middle_name"].strip() not in ["", "NA"]) else ""
                    print('......................fgdffgfghg9')
                    self.__result_dict.last_name              = api_response_data["user_last_name"] if ("user_last_name" in api_response_data.keys() and api_response_data["user_last_name"].strip() not in ["", "NA"]) else "Data Not Available"
                    print('......................fgdffgfghg10')
                    self.__result_dict.aadhaar_seeding_status = api_response_data["aadhaar_seeding_status"] if ("aadhaar_seeding_status" in api_response_data.keys() and api_response_data["aadhaar_seeding_status"].strip() not in ["", "NA"]) else "Data Not Available"      
                    print('......................fgdffgfghg.............')
                elif str(api_response["response_code"]) in ("101","102","103"):
                    print('......................fgdffgfghg11')
                    self.__result_dict.response_code = "103"
                else:
                    self.__result_dict.response_code = "110"
            elif str(response.status_code) == "400":
                if str(api_response["response_code"]) == "106":
                    self.__result_dict.response_code = "102"
                elif str(api_response["response_code"]) == "105":
                    self.__result_dict.response_code = "104"
                elif str(api_response["response_code"]) == "104":
                    self.__result_dict.response_code = "105"
            elif str(response.status_code) == "500":
                self.__result_dict.response_code = "110"
            elif str(response.status_code) in ["503","504"]:
                self.__result_dict.response_code = "110"
            else:
                self.__result_dict.response_code = "110"
        # except Exception as ex:
        #     #print_debug_msg(f"Error occured due to {ex}")
        #     print('Welcome.............')
    
        
        #self.__result_dict.date_time              = str(dt.now().strftime("%Y-%m-%d %H:%M:%S"))
    @property
    def result(self):
        return self.__result_dict

    @property
    def metadata(self):
        return self.__response_metadata
        
def Pan_TH(Name=None, FathersName=None, DOB=None, PAN_number=None, image_text=None, image_base64=None):
    print("TRIGGER AND HYGINE")

    H_1 = "Input/Image customer name matched with the source data"
    H_2 = "Input/Image date of birth matched   with the source data"
    H_3 = "Input/Image pan number validated with the source data"
    H_4 = "Input/Image father's name matched with the source data"

    IMAGE    = False
    text_ = ""
    if image_text != None:
        text_ = image_text
        IMAGE = True
        H_1 = "Customer Name in image matched with the source data"
        H_2 = "Date of Birth in image matched with the source data"
        H_3 = "Pan Number in image validated with the source data"
        H_4 = "Father's Name in image matched with the source data"
    if image_base64 != None:
        #text_ = bytes_to_text(img_data=image_base64)
        text_={}
        IMAGE = True
        H_1 = "Pan input customer name matched with the source data"
        H_2 = "Pan input date of birth matched with the source data"
        H_3 = "Pan input pan number validated with the source data"
        H_4 = "Pan input father's name matched with the source data"

    T_1 = "In PAN number first five values are characters"
    T_2 = "In PAN number six to ninth value are digits"
    T_3 = "In PAN number fourth character is 'P'"
    T_4 = "In PAN number last character is Alphabet"
    # T_5 = "Work experience is okay as per DOB (Age - Experience > 18)"

    #RESULT VALUE
    #HYGIENES
    H_1_SERVICE_RESULT = "N/A"
    H_2_SERVICE_RESULT = "N/A"
    H_3_SERVICE_RESULT = "N/A"
    H_4_SERVICE_RESULT = "N/A"


    if FathersName["SERVICE"].strip() and FathersName["FORM"].strip():
        if FathersName["SERVICE"].startswith("MR "):
            name_percentage = nameMatch(FathersName["FORM"].upper(), FathersName["SERVICE"][3:])
            if "Matched" in name_percentage[0]:
                H_4_SERVICE_RESULT = name_percentage[0]
            else:
                H_4_SERVICE_RESULT = float(name_percentage[0].replace(" %", ""))
        else:
            name_percentage = nameMatch(FathersName["FORM"].upper(), FathersName["SERVICE"])
            if "Matched" in name_percentage[0]:
                H_4_SERVICE_RESULT = name_percentage[0]
            else:
                H_4_SERVICE_RESULT = float(name_percentage[0].replace(" %", "")) 

    if Name["SERVICE"].strip() and Name["FORM"].strip():
        if Name["SERVICE"].startswith("MR ") or Name["SERVICE"].startswith("MS ") or Name["SERVICE"].startswith("MRS "):
            if Name["SERVICE"].startswith("MRS "):
                name_percentage = nameMatch(Name["FORM"].upper(), Name["SERVICE"][4:])
                if "Matched" in name_percentage[0]:
                    H_1_SERVICE_RESULT = name_percentage[0]
                else:
                    H_1_SERVICE_RESULT = float(name_percentage[0].replace(" %", ""))
            else:
                name_percentage = nameMatch(Name["FORM"].upper(), Name["SERVICE"][3:])
                if "Matched" in name_percentage[0]:
                    H_1_SERVICE_RESULT = name_percentage[0]
                else:
                    H_1_SERVICE_RESULT = float(name_percentage[0].replace(" %", ""))
        else:
            name_percentage = nameMatch(Name["FORM"].upper(), Name["SERVICE"])
            if "Matched" in name_percentage[0]:
                H_1_SERVICE_RESULT = name_percentage[0]
            else:
                H_1_SERVICE_RESULT = float(name_percentage[0].replace(" %", ""))

    if DOB["FORM"] and DOB["SERVICE"].strip():
        if DOB["FORM"] != DOB["SERVICE"].strip():
            H_2_SERVICE_RESULT = "NO"
        else:
            H_2_SERVICE_RESULT = "Yes"

    if PAN_number["FORM"] and PAN_number["SERVICE"].strip():
        if PAN_number["FORM"] != PAN_number["SERVICE"].strip():
            H_3_SERVICE_RESULT = "NO"
        else:
            H_3_SERVICE_RESULT = "Yes"

    # if IMAGE:
    #     if Name["FORM"].upper() not in text_:
    #         H_1_IMAGE_RESULT = False
    #     if DOB["FORM"].replace("-","/") not in text_:
    #         H_2_IMAGE_RESULT = False
    #     if PAN_number["FORM"] not in text_:
    #         H_3_IMAGE_RESULT = False
    #     if FathersName["FORM"]:
    #         if FathersName["FORM"].upper() not in text_:
    #             H_4_IMAGE_RESULT = False
    #     else:
    #         H_4_IMAGE_RESULT = "N/A"

    HYGIENES = {
        H_1: {"SERVICE" : H_1_SERVICE_RESULT},
        H_2: {"SERVICE" : H_2_SERVICE_RESULT},
        H_3: {"SERVICE" : H_3_SERVICE_RESULT},
        H_4: {"SERVICE" : H_4_SERVICE_RESULT}
    }

    #TRIGGERS ...
    if (PAN_number["FORM"][:5].isalpha()):
        T_1_RESULT = True
    else:
        T_1_RESULT = False
    if (PAN_number["FORM"][6:9].isnumeric()):
        T_2_RESULT = True
    else:
        T_2_RESULT = False
    if (PAN_number["FORM"][3]=="P"):
        T_3_RESULT = True
    else:
        T_3_RESULT = False
    if (PAN_number["FORM"][-1].isalpha()):
        T_4_RESULT = True
    else:
        T_4_RESULT = False
    # date_today = dt.date(dt.today())
    # date_dob = dt.date(dt.strptime(str(DOB["FORM"]).strip(), '%d-%m-%Y'))
    # date_diffr = date_today - date_dob
    # if (date_diffr.days//365 >= 18):
    #     T_5_RESULT = True
    # else:
    #     T_5_RESULT = False
    
    PAN_FOUND_IN_IMAGE = True if PAN_number["FORM"] in text_.replace(' ', '') else False

    TRIGGERS = {
        T_1 : { "SERVICE" : "N/A" if not PAN_number["SERVICE"] else "Yes" if PAN_number["SERVICE"][:5].isalpha() else "NO", "IMAGE" : "N/A" if (not IMAGE or not PAN_number["FORM"]) else "Yes" if (IMAGE and PAN_FOUND_IN_IMAGE and T_1_RESULT) else "NO" }, 
        T_2 : { "SERVICE" : "N/A" if not PAN_number["SERVICE"] else "Yes" if PAN_number["SERVICE"][6:9].isnumeric() else "NO", "IMAGE" : "N/A" if (not IMAGE or not PAN_number["FORM"]) else "Yes" if (IMAGE and PAN_FOUND_IN_IMAGE and T_2_RESULT) else "NO" }, 
        T_3 : { "SERVICE" : "N/A" if not PAN_number["SERVICE"] else "Yes" if PAN_number["SERVICE"][3]=="P" else "NO", "IMAGE" : "N/A" if (not IMAGE or not PAN_number["FORM"]) else "Yes" if (IMAGE and PAN_FOUND_IN_IMAGE and T_3_RESULT) else "NO" }, 
        T_4 : { "SERVICE" : "N/A" if not PAN_number["SERVICE"] else "Yes" if PAN_number["SERVICE"][-1].isalpha() else "NO", "IMAGE" : "N/A" if (not IMAGE or not PAN_number["FORM"]) else "Yes" if (IMAGE and PAN_FOUND_IN_IMAGE and T_4_RESULT) else "NO" },  
    }

    T_H = {
        "TRIGGERS" : {"DATA" : TRIGGERS},
        "HYGIENES" : {"DATA" : HYGIENES}
    }

    return T_H

def panCall(analysis_mode: bool=False, application_data: Munch=None, application_meta: Munch=None, api_mode: bool=False, service_type=""):
    pan        = application_data.pan.strip()
    name       = application_data.name.strip() if 'name' in application_data.keys() and len(application_data['name'])>0 else ''
    dob        = application_data.dob.strip()  if 'dob' in application_data.keys() and len(application_data['dob'])>0 else ''
    PAN_RESULT = {}
    RESP_CODE  = ""
    # try   :
    transaction = []
    api_called = ""
    if (str(pan).strip() != '' and pan != None):
        PAN_RESULT["response_code"] = ""
        if service_type=="IDR":
            #PAN_RESULT = CKYC_verification.CKYC(pan, dob)
            if not api_mode:
                application_meta.response_metadata = PAN_RESULT.metadata
            PAN_RESULT = PAN_RESULT.result
            
        if PAN_RESULT["response_code"] == "101":
            api_called = "CKYC"
            PAN_RESULT["first_name"]=PAN_RESULT["USER_FIRST_NAME"] if ("USER_FIRST_NAME" in PAN_RESULT.keys() and PAN_RESULT["USER_FIRST_NAME"].strip() not in ["", "N/A"]) else ""
            PAN_RESULT["middle_name"]=''
            PAN_RESULT["last_name"]=PAN_RESULT["USER_LAST_NAME"] if ("USER_LAST_NAME" in PAN_RESULT.keys() and PAN_RESULT["USER_LAST_NAME"].strip() not in ["", "N/A"]) else ""
            PAN_RESULT["user_pan"]=PAN_RESULT["USER_PAN_NUMBER"] if ("USER_PAN_NUMBER" in PAN_RESULT.keys() and PAN_RESULT["USER_PAN_NUMBER"].strip() not in ["", "N/A"]) else ""
            PAN_RESULT["user_dob"]=PAN_RESULT["USER_DOB"] if ("USER_DOB" in PAN_RESULT.keys() and PAN_RESULT["USER_DOB"].strip() not in ["", "N/A"]) else ""
            PAN_RESULT["name_on_card"]=PAN_RESULT["USER_FULL_NAME"] if ("USER_FULL_NAME" in PAN_RESULT.keys() and PAN_RESULT["USER_FULL_NAME"].strip() not in ["", "N/A"]) else ""
            PAN_RESULT["fathers_name"]=PAN_RESULT["FATHER_FULL_NAME"] if ("FATHER_FULL_NAME" in PAN_RESULT.keys() and PAN_RESULT["FATHER_FULL_NAME"].strip() not in ["", "N/A"]) else ""
            RESP_CODE = "101"

        else:
            PAN_RESULT = {}
            T_ADVANCE = Pan(pan)
            #T_PRO  = PAN_Pro(pan)
            T_ADVANCE_RESULT = T_ADVANCE.result
            PAN_RESULT.update(T_ADVANCE_RESULT)
            RESP_CODE = "101" if T_ADVANCE_RESULT.response_code == "101" else "110"
        # PAN_RESULT['name_match']="N/A"
        # PAN_RESULT['dob_match']="N/A"
        # first_name=PAN_RESULT["first_name"] if PAN_RESULT["first_name"] not in 'Data Not Available' else ''
        # middle_name=' '+PAN_RESULT["middle_name"] if 'middle_name' in PAN_RESULT.keys() and len(PAN_RESULT["middle_name"])>0 else ''
        # last_name=PAN_RESULT["last_name"] if PAN_RESULT["last_name"] not in 'Data Not Available' else ''
        if analysis_mode:
            name         = application_data.name
            fathers_name = application_data.father_name
            if service_type=="IDR":
                image_text = application_data.image_text
                image      = None if image_text else application_data.image
            else:
                image_text = None
                image      = application_data.image
            dob          = application_data.dob
            PAN_T_H = {}
            
            try   : USER_PAN = PAN_RESULT["user_pan"] if "user_pan" in PAN_RESULT.keys() else PAN_RESULT["pan_number"]
            except: USER_PAN = ""
            try   : USER_DOB = PAN_RESULT["user_dob"]
            except: USER_DOB = ""
            PAN_T_H = Pan_TH(
                Name         = { "FORM": name.upper(), "SERVICE": PAN_RESULT["name_on_card"].upper() if (PAN_RESULT["name_on_card"] and "name_on_card" in PAN_RESULT.keys()) else (PAN_RESULT["first_name"]+PAN_RESULT["middle_name"]+PAN_RESULT["last_name"]).upper() if ("first_name" in PAN_RESULT.keys() and "middle_name" in PAN_RESULT.keys() and "last_name" in PAN_RESULT.keys()) else ""}, 

                FathersName  = { "FORM": fathers_name.upper(), "SERVICE": PAN_RESULT["fathers_name"].upper() if ("fathers_name" in PAN_RESULT.keys() and PAN_RESULT["fathers_name"]) else (PAN_RESULT["FATHER_FIRST_NAME"]+PAN_RESULT["FATHER_LAST_NAME"]).upper() if ("FATHER_FIRST_NAME" in PAN_RESULT.keys() and "FATHER_LAST_NAME" in PAN_RESULT.keys()) else "" },

                DOB          = { "FORM": dob, "SERVICE": USER_DOB },
                PAN_number   = { "FORM": pan.upper(), "SERVICE": USER_PAN },
                image_text = image_text,
                image_base64 = image
            )
            PAN_RESULT["T_H"] = PAN_T_H
    else:
        RESP_CODE = "102"
        if not api_mode:
            application_meta.response_metadata = {}
    billing_details = billable_and_response_msg(response_code=RESP_CODE)
    if len(name)>0 and billing_details['BILLABLE']=='True' and str(RESP_CODE)=='101':
       pass
    #    name_service=first_name+middle_name+' '+last_name
    #    NAME_MATCH_PERCENTAGE_SERVICE = getMatchPercent(OCR_TEXT=name.upper(), ADDRESS_STR=name_service.upper())
    #    if NAME_MATCH_PERCENTAGE_SERVICE == 100:
    #       NAME_MATCH_PERCENTAGE_SERVICE = getMatchPercent(OCR_TEXT=name_service.upper(), ADDRESS_STR=name.upper())
    #       if NAME_MATCH_PERCENTAGE_SERVICE == 100:
    #         PAN_RESULT['name_match']='Matched'
    #       else:
    #          PAN_RESULT['name_match']= str(NAME_MATCH_PERCENTAGE_SERVICE)+' %'
    #    else:
    #        pass
            #NAME_MATCH_PERCENTAGE_SERVICE_1 = getMatchPercent(OCR_TEXT=name_service.upper(), ADDRESS_STR=name.upper())
            #PAN_RESULT['name_match']= str(NAME_MATCH_PERCENTAGE_SERVICE)+' %' if NAME_MATCH_PERCENTAGE_SERVICE<=NAME_MATCH_PERCENTAGE_SERVICE_1 else str(NAME_MATCH_PERCENTAGE_SERVICE_1)+' %'
    #    if len(dob.strip())>0:
    #         if dob==PAN_RESULT["user_dob"]:
    #             PAN_RESULT['dob_match']="YES"
    #         else:
    #             PAN_RESULT['dob_match']="NO"


    if not api_mode:
        application_meta.response_metadata["input_data"]            = {}
        application_meta.response_metadata["input_data"]["pan"]     = application_data.pan

        if analysis_mode:
            transaction.append({
                            "api": "PAN_FRAUD",
                            "billable": billing_details["BILLABLE"],
                            "response_code": RESP_CODE,
                        })
        else:
            transaction.append({
                            "api": "PAN",
                            "billable": billing_details["BILLABLE"],
                            "response_code": RESP_CODE,
                        })
                    
        # transactions_log.objects.enter_trx_log(
        #         application_number = application_meta.application_number, 
        #         login_id           = application_meta.login_id, 
        #         product            = application_meta.product,
        #         state              = application_meta.state,
        #         transactions       = transaction, 
        #         transactions_type  = application_meta.transactions_type,
        #         response_metadata  = application_meta.response_metadata,
        #         request_id         = application_data.request_id if 'request_id' in application_data.keys() else ''
        #     )
    
         
    return PAN_RESULT,billing_details["BILLABLE"], RESP_CODE, billing_details["MESSAGE"], api_called