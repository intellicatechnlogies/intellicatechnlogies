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
# from core.components.API.clients.Email_send_dev import send_email_code_exception_record 

class VOTER_ID:
    def __init__(self,epic_no = "",rec_id=None, meta_data=None):
        self.__epic_no = epic_no
        #Get Result of the Voter id
        self.__result_dict = Munch()
        self.__result_dict.response_code                                                                      = "110"
        self.__result_dict.EPIC_Voter_ID_Number                                                               = ""
        self.__result_dict.Name_of_the_card_holder                                                            = ""
        self.__result_dict.Name_of_relative                                                                   = ""
        self.__result_dict.Relative_type                                                                      = ""
        self.__result_dict.Card_holders_gender                                                                = ""
        self.__result_dict.Card_holders_email_id                                                              = ""
        self.__result_dict.Card_holder_mobile_number                                                          = ""
        self.__result_dict.Card_holders_age                                                                   = ""
        self.__result_dict.Card_holders_date_of_birth                                                         = ""
        self.__result_dict.Card_holders_house_number                                                          = ""
        self.__result_dict.Name_of_the_part_Location_in_the_constituency_applicable_to_the_card_holder        = ""
        self.__result_dict.Parliamentary_Constituency_applicable_to_the_card_holder                           = ""
        self.__result_dict.Parliamentary_Constituency_Number                                                  = ""
        self.__result_dict.Constituency_applicable_to_the_card_holder                                         = ""
        self.__result_dict.Constituency_Number                                                                = ""
        self.__result_dict.Assembly_Constituency_applicable_to_the_card_holder                                = ""
        self.__result_dict.Assembly_Constituency_Number                                                       = ""
        self.__result_dict.District_of_the_Electoral_Office                                                   = ""
        self.__result_dict.District_code                                                                      = ""
        self.__result_dict.State_of_the_registered_Electoral_Office                                           = ""
        self.__result_dict.State_Code                                                                         = ""
        self.__result_dict.Number_of_the_part_location_in_the_constituency_applicable_to_the_card_holder      = ""
        self.__result_dict.Lat_Long_for_the_polling_booth_applicable_to_the_card_holder                       = ""
        self.__result_dict.Lat_Long_0_coordinate                                                              = ""
        self.__result_dict.Lat_Long_1_coordinate                                                              = ""
        self.__result_dict.Polling_Booth_Address_applicable_for_the_card_holder                               = ""
        self.__result_dict.Polling_Booth_Address_Number_applicable_for_the_card_holder                        = ""
        self.__result_dict.Section_of_the_constituency_part_applicable_to_the_card_holder                     = ""
        self.__result_dict.Serial_number_of_the_card_holder_in_the_polling_list_in_the_applicable_part        = ""
        self.__result_dict.Unique_ID_of_the_card_holder                                                       = ""
        self.__result_dict.Last_date_of_update_to_the_records_against_the_given_epic_no_in_Government_Records = ""
        self.__result_dict.Voter_Application_Status                                                           = ""

        self.__result_dict.epic_no                                                                            = epic_no
        self.__result_dict.date_time                                                                          = ""
        self.__response_metadata                                                                              = Munch()
        self.getVoterID_result(rec_id=rec_id, meta_data=meta_data)

    def getVoterID_result(self,rec_id, meta_data):
        try:
            # base_url = config.zoop_base_url["base_url"]
            # url = f"{base_url}/in/identity/voter/advance"

            # payload = dump_as_JSON({
            # "data": {
            #     "customer_epic_number": self.__epic_no ,
            #     "consent": "Y",
            #     "consent_text": "Approve the values here"
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
            api_response={}
            self.__response_metadata = {key : value for key,value in api_response.items() if key != "result"}
            if str(response.status_code) == "200":
                if str(api_response["response_code"]) == "100":
                    api_response_data = api_response["result"]
                    self.__result_dict.response_code = "101"
                    if "address" in api_response_data.keys():
                        address_response_data = api_response_data["address"]
                        #self.__result_dict.District_of_the_Electoral_Office                                                   = (address_response_data["district_name"] if ("district_name" in address_response_data.keys() and str(address_response_data["district_name"]).strip() not in ["", "N/A"]) else "N/A") + (f" ({address_response_data['district_name_vernacular']})" if "district_name_vernacular" in address_response_data.keys() and address_response_data["district_name_vernacular"].strip() not in ["", "N/A"] else "") 
                        self.__result_dict.District_of_the_Electoral_Office                                                   = address_response_data["district_name"] if ("district_name" in address_response_data.keys() and str(address_response_data["district_name"]).strip() not in ["", "N/A"]) else "N/A"
                        self.__result_dict.District_code                                                                      = address_response_data["district_code"] if ("district_code" in address_response_data.keys() and str(address_response_data["district_code"]).strip() not in ["","N/A"]) else "N/A"
                        self.__result_dict.State_of_the_registered_Electoral_Office                                           = address_response_data["state"] if ("state" in address_response_data.keys() and str(address_response_data["state"]).strip() not in ["", "N/A"]) else "N/A"
                        self.__result_dict.State_Code                                                                         = address_response_data["state_code"] if ("state_code" in address_response_data.keys() and str(address_response_data["state_code"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.EPIC_Voter_ID_Number                                                               = api_response_data["epic_number"] if ("epic_number" in api_response_data.keys() and str(api_response_data["epic_number"]).strip() not in ["","N/A"]) else "N/A"
                    # self.__result_dict.Name_of_the_card_holder                                                            = (api_response_data["user_name_english"].strip() if ("user_name_english" in api_response_data.keys() and str(api_response_data["user_name_english"]).strip() not in ["", "N/A"]) else "N/A") + (f" ({api_response_data['user_name_vernacular'].strip()})" if "user_name_vernacular" in api_response_data.keys() and api_response_data["user_name_vernacular"].strip() not in ["", "N/A"] else "")
                    self.__result_dict.Name_of_the_card_holder                                                            = str(api_response_data["user_name_english"]).strip() if ("user_name_english" in api_response_data.keys() and str(api_response_data["user_name_english"]).strip() not in ["", "N/A"]) else "N/A"
                    # self.__result_dict.Name_of_relative                                                                   = (api_response_data["relative_name_english"].strip() if ("relative_name_english" in api_response_data.keys() and str(api_response_data["relative_name_english"]).strip() not in ["", "N/A"]) else "N/A") + (f" ({api_response_data['relative_name_vernacular'].strip()})" if "relative_name_vernacular" in api_response_data.keys() and api_response_data["relative_name_vernacular"].strip() not in ["", "N/A"] else "")
                    self.__result_dict.Name_of_relative                                                                   = str(api_response_data["relative_name_english"]).strip() if ("relative_name_english" in api_response_data.keys() and str(api_response_data["relative_name_english"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Relative_type                                                                      = api_response_data["relative_relation"] if ("relative_relation" in api_response_data.keys() and str(api_response_data["relative_relation"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Card_holders_gender                                                                = api_response_data["user_gender"] if ("user_gender" in api_response_data.keys() and str(api_response_data["user_gender"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Card_holders_email_id                                                              = api_response_data["email_id"] if ("email_id" in api_response_data.keys() and str(api_response_data["email_id"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Card_holder_mobile_number                                                          = api_response_data["mob_no"] if ("mob_no" in api_response_data.keys() and str(api_response_data["mob_no"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Card_holders_age                                                                   = api_response_data["user_age"] if ("user_age" in api_response_data.keys() and api_response_data["user_age"] not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Card_holders_date_of_birth                                                         = api_response_data["dob"] if ("dob" in api_response_data.keys() and str(api_response_data["dob"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Card_holders_house_number                                                          = api_response_data["house_no"] if ("house_no" in api_response_data.keys() and api_response_data["house_no"] not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Name_of_the_part_Location_in_the_constituency_applicable_to_the_card_holder        = str(api_response_data["part_name"]).strip() if ("part_name" in api_response_data.keys() and str(api_response_data["part_name"]).strip() not in ["", "N/A"]) else "N/A"
                    # self.__result_dict.Constituency_applicable_to_the_card_holder                                         = (api_response_data["constituency_part_name"] if ("constituency_part_name" in api_response_data.keys() and str(api_response_data["constituency_part_name"]).strip() not in ["", "N/A"]) else "N/A") + (f" ({api_response_data['constituency_part_name_vernacular']})" if "constituency_part_name_vernacular" in api_response_data.keys() and api_response_data["constituency_part_name_vernacular"].strip() not in ["", "N/A"] else "")
                    self.__result_dict.Constituency_applicable_to_the_card_holder                                         = api_response_data["constituency_part_name"] if ("constituency_part_name" in api_response_data.keys() and str(api_response_data["constituency_part_name"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Constituency_Number                                                                = api_response_data["constituency_part_number"] if ("constituency_part_number" in api_response_data.keys() and str(api_response_data["constituency_part_number"]).strip() not in ["", "N/A"]) else "N/A"
                    # self.__result_dict.Assembly_Constituency_applicable_to_the_card_holder                                = (api_response_data["assembly_constituency_name"] if ("assembly_constituency_name" in api_response_data.keys() and str(api_response_data["assembly_constituency_name"]).strip() not in ["", "N/A"]) else "N/A") + (f" ({api_response_data['assembly_constituency_name_vernacular']})" if "assembly_constituency_name_vernacular" in api_response_data.keys() and api_response_data["assembly_constituency_name_vernacular"].strip() not in ["", "N/A"] else "") 
                    self.__result_dict.Assembly_Constituency_applicable_to_the_card_holder                                = api_response_data["assembly_constituency_name"] if ("assembly_constituency_name" in api_response_data.keys() and str(api_response_data["assembly_constituency_name"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Assembly_Constituency_Number                                                       = api_response_data["assembly_constituency_number"] if ("assembly_constituency_number" in api_response_data.keys() and str(api_response_data["assembly_constituency_number"]).strip() not in ["", "N/A"]) else "N/A"                         
                    # self.__result_dict.Parliamentary_Constituency_applicable_to_the_card_holder                           = (api_response_data["parliamentary_constituency_name"].strip() if ("parliamentary_constituency_name" in api_response_data.keys() and str(api_response_data["parliamentary_constituency_name"]).strip() not in ["", "N/A"]) else "N/A") + (f" ({api_response_data['parliamentary_constituency_name_vernacular'].strip()})" if "parliamentary_constituency_name_vernacular" in api_response_data.keys() and api_response_data["parliamentary_constituency_name_vernacular"].strip() not in ["", "N/A"] else "" )
                    self.__result_dict.Parliamentary_Constituency_applicable_to_the_card_holder                           = str(api_response_data["parliamentary_constituency_name"]).strip() if ("parliamentary_constituency_name" in api_response_data.keys() and str(api_response_data["parliamentary_constituency_name"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Parliamentary_Constituency_Number                                                  = api_response_data["parliamentary_constituency_number"] if ("parliamentary_constituency_number" in api_response_data.keys() and str(api_response_data["parliamentary_constituency_number"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Section_of_the_constituency_part_applicable_to_the_card_holder                     = api_response_data["constituency_section_number"] if ("constituency_section_number" in api_response_data.keys() and str(api_response_data["constituency_section_number"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Serial_number_of_the_card_holder_in_the_polling_list_in_the_applicable_part        = api_response_data["serial_number_applicable_part"] if ("serial_number_applicable_part" in api_response_data.keys() and str(api_response_data["serial_number_applicable_part"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Last_date_of_update_to_the_records_against_the_given_epic_no_in_Government_Records = api_response_data["voter_last_updated_date"] if ("voter_last_updated_date" in api_response_data.keys() and str(api_response_data["voter_last_updated_date"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.Voter_Application_Status                                                           = api_response_data["status"] if ("status" in api_response_data.keys() and str(api_response_data["status"]).strip() not in ["", "N/A"]) else "N/A"
                    self.__result_dict.date_time                                                                          = str(dt.now().strftime("%Y-%m-%d %H:%M:%S")) 
                    if "polling_booth" in api_response_data.keys():
                        polling_booth = api_response_data["polling_booth"]
                        self.__result_dict.Lat_Long_for_the_polling_booth_applicable_to_the_card_holder                       = polling_booth["lat_long"] if ("lat_long" in polling_booth.keys() and str(polling_booth["lat_long"]).strip() not in ["", "N/A"]) else "N/A"
                        # self.__result_dict.Polling_Booth_Address_applicable_for_the_card_holder                               = (polling_booth["name"].strip() if ("name" in polling_booth.keys() and str(polling_booth["name"]).strip() not in ["", "N/A"]) else "N/A") + (f" ({polling_booth['name_vernacular'].strip()})" if "name_vernacular" in polling_booth.keys() and polling_booth["name_vernacular"].strip() not in ["", "N/A"] else "" )
                        self.__result_dict.Polling_Booth_Address_applicable_for_the_card_holder                               = str(polling_booth["name"]).strip() if ("name" in polling_booth.keys() and str(polling_booth["name"]).strip() not in ["", "N/A"]) else "N/A"
                        self.__result_dict.Polling_Booth_Address_Number_applicable_for_the_card_holder                        = polling_booth["number"] if ("number" in polling_booth.keys() and str(polling_booth["number"]).strip() not in ["", "N/A"]) else "N/A"
                elif str(api_response["response_code"]) in ("101","102","103"):
                    self.__result_dict.response_code = "103"
                else:
                    self.__result_dict.response_code = "110"
            elif str(response.status_code) == "400":
                if str(api_response["response_code"]) == "106":
                    self.__result_dict.response_code = "102"
                elif str(api_response["response_code"]) == "105":
                    self.__result_dict.response_code = "110"
                elif str(api_response["response_code"]) == "104":
                    self.__result_dict.response_code = "110"
                else:
                    self.__result_dict.response_code = "110"
            elif str(response.status_code) == "500":
                if str(api_response["response_code"]) == "99":
                    self.__result_dict.response_code = "110"
                elif str(api_response["response_code"]) == "111":
                    self.__result_dict.response_code = "110"
            elif str(response.status_code) == "503":
                if str(api_response["response_code"]) == "110":
                    self.__result_dict.response_code = "110"
            else:
                self.__result_dict.response_code = "110"
        except Exception as ex:
             self.__result_dict = Munch(map(lambda item: (item, '' if(item != 'epic_no') else self.__result_dict[item]), self.__result_dict.keys()))      
             self.__result_dict.response_code ="110"
            #  send_email_code_exception_record(api_response={"record_id":rec_id,"meta_data":meta_data,"error_code":f"exception of code {ex}"})
            #  print_debug_msg(f"Error occured due to {ex}")

    @property
    def result(self):
        return self.__result_dict

    @property
    def metadata(self):
        return self.__response_metadata

def getAddrMatchPercent(OCR_TEXT: str=None, ADDRESS_STR: str=None):
    OCR_KWDS  = OCR_TEXT.strip().replace(",","").split(" ")
    ADDR_KWDS = ADDRESS_STR.strip().replace(",","").split(" ")
    matches = []
    for KWD_A in ADDR_KWDS:
        closeMatch = get_close_matches(word=KWD_A, possibilities=OCR_KWDS, n=1)
        if len(closeMatch) == 1:
            matches.append(SequenceMatcher(a=KWD_A, b=closeMatch[0]).ratio())
        else:
            matches.append(0.0)

    return (sum(matches)*100)//len(ADDR_KWDS)

def VOTER_ID_TH(Name: str=None, FathersName: str=None, DOB: str=None, gender: str=None,voterid: str=None, pin: str=None, city: str=None, state: str=None, address: str=None, image_base64_front: str=None,image_base64_back: str=None):
    IMAGE = False
    if image_base64_front:
        IMAGE = True
        text_back= bytes_to_text(img_data=image_base64_back) if image_base64_back !=None and len(image_base64_back)>0 else ''
        textimage_ = bytes_to_text(img_data=image_base64_front)+ text_back
    #STATE NAME
    state_name=["ANDHRA PRADEST","ARUNACHAL PRADESH","ASSAM","BIHAR","CHHATTISGARH","GOA","GUJARAT","HARYANA","HIMACHAL PRADESH","JAMMU AND KASHMIR","JHARKHAND","KARNATAKA","KERLA","MADHYA PRADESH","MAHARASHTRA","MANIPUR","MEGHALAYA","MIZORAM","NAGALAND","ODISHA","PUNJAB","RAJASTHAN","SIKKIM","TAMIL NADU","TELANGANA","TRIPURA","UTTARAKHAND","UTTAR PRADESH","WEST BENGAL","ANDAMAN AND NICOBAR ISLANDS","CHANDIGARGH","DADRA AND NAGAR HAVELI","DAMAN AND DIU","DELHI","LAKSHADWEEP","PUDUCHERRY"]
    # SCORE CALCULATION...
    # HYGIENES
    H_1_SERVICE_SCORE, H_1_IMAGE_SCORE = (0.060, 0.060) if IMAGE else (0.12, "N/A")
    H_2_SERVICE_SCORE, H_2_IMAGE_SCORE = (0.110, 0.110) if IMAGE else (0.22, "N/A")
    H_3_SERVICE_SCORE, H_3_IMAGE_SCORE = (0.055, 0.055) if IMAGE else (0.11, "N/A")
    H_4_SERVICE_SCORE, H_4_IMAGE_SCORE = (0.055, 0.055) if IMAGE else (0.11, "N/A")
    H_5_SERVICE_SCORE, H_5_IMAGE_SCORE = (0.055, 0.055) if IMAGE else (0.11, "N/A")
    H_6_SERVICE_SCORE, H_6_IMAGE_SCORE = (0.055, 0.055) if IMAGE else (0.11, "N/A")
    H_7_SERVICE_SCORE, H_7_IMAGE_SCORE = (0.055, 0.055) if IMAGE else (0.11, "N/A")
    H_8_SERVICE_SCORE, H_8_IMAGE_SCORE = (0.055, 0.055) if IMAGE else (0.11, "N/A")
    H_9_SERVICE_SCORE, H_9_IMAGE_SCORE = (0.055, 0.055) if IMAGE else (0.11, "N/A")

    H_S_SCORE, H_I_SCORE = 0, 0
    
    H_1 = "Customer's name matched in VoterID"
    H_2 = "Customer's Father name matched in VoterID"
    H_3 = "Gender matched in VoterID"
    H_4 = "Date of birth matched in VoterID"
    H_5 = "VoterID number matched in VoterID"
    H_6 = "Pincode matched in VoterID"
    H_7 = "City matched in VoterID"
    H_8 = "State matched in VoterID"
    H_9 = "Customer's Address matched in VoterID"

    # Customer's name matched in VoterID
    if Name["FORM"] != Name["SERVICE"]:
        H_1_SERVICE_SCORE = 0.0
    if IMAGE:
            if(not (search_text("\\b" + Name["FORM"].upper() + "\\b", textimage_.upper()))):
            # if Name["FORM"] not in textimage_:
                H_1_IMAGE_SCORE = 0.0
    
    # Customer's Father name matched in VoterID
    if FathersName["FORM"] != FathersName["SERVICE"]:
            H_2_SERVICE_SCORE = 0
    if IMAGE:
                if(not (search_text("\\b" + FathersName["FORM"].upper() + "\\b", textimage_.upper()))):
                # if FathersName["FORM"] not in textimage_:
                    H_2_IMAGE_SCORE = 0.0
    
    #Gender
    if gender["FORM"][0] != gender["SERVICE"]:
            H_3_SERVICE_SCORE = 0
    if IMAGE:
                if(not (search_text("\\b" + gender["FORM"].upper() + "\\b", textimage_.upper()))):
                # if gender["FORM"] not in textimage_:
                    H_3_IMAGE_SCORE = 0.0
    # Date of birth matched in VoterID
    H_4_SERVICE_SCORE=0.0
    if(search_text("\\b" + 'AGE AS ON 1.1' + "\\b", textimage_.upper())):
    # if 'AGE AS ON 1.1' in textimage_:
        H_4_IMAGE_SCORE = -1.0
    elif IMAGE:
        #if (DOB["FORM"] not in textfront_ and DOB["FORM"].replace("-","/") not in textfront_) and (DOB["FORM"].replace("-","/") not in textback_ or DOB["FORM"].replace("-","/") not in textback_):
        H_4_IMAGE_SCORE=H_4_IMAGE_SCORE if(search_text("\\b" + DOB["FORM"] + "\\b", textimage_.upper())) else H_4_IMAGE_SCORE if(search_text("\\b" + DOB["FORM"].replace("-","/") + "\\b", textimage_.upper())) else 0.0
        # H_4_IMAGE_SCORE = H_4_IMAGE_SCORE if DOB["FORM"]  in textimage_ or DOB["FORM"].replace("-","/")  in textimage_ else 0.0

    # VoterID number matched in VoterID
    if voterid["FORM"] != voterid["SERVICE"]:
        H_4_SERVICE_SCORE = 0
    if IMAGE:
                H_5_IMAGE_SCORE = 0.55
                #H_5_IMAGE_SCORE =H_5_IMAGE_SCORE if voterid["FORM"] in textimage_  else 0.0
                H_5_IMAGE_SCORE  = H_5_IMAGE_SCORE if(search_text("\\b" + voterid["FORM"] + "\\b", textimage_.upper())) else 0.0
   

    # Pincode matched in VoterID
    H_6_SERVICE_SCORE = 0.0
    if IMAGE:
        # if pin["FORM"] not in textimage_:
        if(not search_text("\\b" + pin["FORM"] + "\\b", textimage_.upper())):
            if(pincode_match(state=state["FORM"],city=city["FORM"],image_text=textimage_.upper())):
                H_6_IMAGE_SCORE = 0.0
            else:
                H_6_IMAGE_SCORE = -1.0
        else:
            H_6_IMAGE_SCORE = 0.55


    
    # City matched in VoterID
    if city["FORM"] not in city["SERVICE"]:
        H_7_SERVICE_SCORE = 0
    if IMAGE:
        if(not search_text("\\b" + city["FORM"] + "\\b", textimage_.upper())):
        # if city["FORM"] not in textimage_:
            H_7_IMAGE_SCORE = 0.0
    
    # State matched in VoterID
    if state["FORM"] not in state["SERVICE"]:
        H_8_SERVICE_SCORE = 0
    else:
        if IMAGE:
            if(not search_text("\\b" + state["FORM"] + "\\b", textimage_.upper())):
            # if state["FORM"] not in textimage_:
                H_8_IMAGE_SCORE = 0.0
    if H_8_IMAGE_SCORE == 0.0:
        for state_ in state_name:
            if(not search_text("\\b" + state_ + "\\b", textimage_.upper())):
            # if state_ not in textimage_:
                H_8_IMAGE_SCORE = -1.0
            else:
                H_8_IMAGE_SCORE = 0.0
                break
    # Customer's Address matched in VoterID
    ADDRESS_MATCH_PERCENTAGE_SERVICE = getAddrMatchPercent(OCR_TEXT=address["SERVICE"], ADDRESS_STR=address["FORM"])
    if ADDRESS_MATCH_PERCENTAGE_SERVICE >= 50.0:
        H_S_SCORE += H_9_SERVICE_SCORE
    else:
        H_9_SERVICE_SCORE=-1.0
    ADDRESS_MATCH_PERCENTAGE_IMAGE = getAddrMatchPercent(OCR_TEXT=textimage_, ADDRESS_STR=address["FORM"])
    if ADDRESS_MATCH_PERCENTAGE_IMAGE >= 50.0:
        H_I_SCORE += H_9_IMAGE_SCORE
    else:
        H_9_IMAGE_SCORE=-1.0


    HYGIENES = {
        H_1: { "SERVICE": "Yes" if bool(H_1_SERVICE_SCORE) else "No", "IMAGE": "Yes" if (IMAGE and H_1_IMAGE_SCORE != 0.0) else "No" },
        H_2: { "SERVICE": "Yes" if bool(H_2_SERVICE_SCORE) else "No", "IMAGE": "Yes" if (IMAGE and H_2_IMAGE_SCORE != 0.0) else "No" },
        H_3: { "SERVICE": "Yes" if bool(H_3_SERVICE_SCORE) else "No", "IMAGE": "Yes" if (IMAGE and H_3_IMAGE_SCORE != 0.0) else "No" },
        H_4: { "SERVICE": "N/A"                                     , "IMAGE": "DOB is not given on submitted document" if (IMAGE and H_4_IMAGE_SCORE == -1.0) else "Yes" if (IMAGE and bool(H_4_IMAGE_SCORE)) else "No" },
        H_5: { "SERVICE": "Yes" if bool(H_5_SERVICE_SCORE) else "No", "IMAGE": "Yes" if (IMAGE and H_5_IMAGE_SCORE != 0.0) else "No" },
        H_6: { "SERVICE": "N/A"                                     , "IMAGE": "Pincode is not given on submitted document as per inputted city" if (IMAGE and H_6_IMAGE_SCORE == -1.0) else "Yes" if (IMAGE and bool(H_6_IMAGE_SCORE)) else "No" },
        H_7: { "SERVICE": "Yes" if bool(H_7_SERVICE_SCORE) else "No", "IMAGE": "Yes" if (IMAGE and H_7_IMAGE_SCORE != 0.0) else "No" },
        H_8: { "SERVICE": "Yes" if bool(H_8_SERVICE_SCORE) else "No", "IMAGE": "State is not given on submitted document" if (IMAGE and H_8_IMAGE_SCORE == -1.0) else "Yes" if (IMAGE and bool(H_8_IMAGE_SCORE)) else "No" },
        H_9: { "SERVICE": "Address Match with "+str(ADDRESS_MATCH_PERCENTAGE_SERVICE)+"%" if (H_9_SERVICE_SCORE == -1.0) else "Yes" if bool(H_9_SERVICE_SCORE) else "No", "IMAGE": "Address Match with "+str(ADDRESS_MATCH_PERCENTAGE_IMAGE)+"%" if (H_9_IMAGE_SCORE == -1.0) else "Yes" if (IMAGE and bool(H_9_IMAGE_SCORE)) else "No" },
    }
   

    return {"HYGIENES": {"DATA": HYGIENES }}

def voterCall(analysis_mode: bool=False, application_data: Munch=None, application_meta:Munch=None,mode:bool=False,record_id=None):
    epic_no = application_data.vid
    VOTER_ID_RESULT = { "DATA": {}, "T_H": {} }
    BILLABLE        = True
    RESP_MSG        = "We found a match for the given VOTER ID number."
    RESP_CODE       = ""

    if (str(epic_no).strip() != '' and epic_no != None):
        VOTER_ID_INSTANCE = VOTER_ID(epic_no, record_id, application_meta)
        VOTER_ID_RESULT   = VOTER_ID_INSTANCE.result
        RESP_CODE         = VOTER_ID_RESULT.response_code
        if not mode:
            application_meta.response_metadata  = VOTER_ID_INSTANCE.metadata
        if VOTER_ID_RESULT.response_code == "101":
            # tmp = {
            #     k.replace("_"," "): v
            #         for k, v in dict(VOTER_ID_RESULT).items()
            # }
            # VOTER_ID_RESULT = tmp

            # del VOTER_ID_RESULT["response_code"]
            
            if analysis_mode:
                address        = application_data["VOTERID_ADDRESS"].replace(",","").strip().upper()
                pin            = application_data["VOTERID_PIN"].strip().upper()
                city           = application_data["VOTERID_CITY"].replace(",","").strip().upper()
                state          = application_data["VOTERID_STATE"].replace(",","").strip().upper()
                voter_front_img= application_data["VOTER_FRONT_IMAGE"]
                voter_back_img = application_data["VOTER_BACK_IMAGE"]
                user_name      = application_data["FIRST_NAME"].replace(",","").strip().upper()
                user_middle    = application_data["MIDDLE_NAME"]
                user_last_name = (application_data["LAST_NAME"].replace(",","").strip() +" "+user_middle).strip().upper()
                fathers_name   = application_data["FATHER_FIRST_NAME"].replace(",","").strip().upper() if len(application_data["FATHER_FIRST_NAME"]) > 0 else None
                dob            = application_data["DOB"].strip()
                gender         = application_data["VOTERID_GENDER"].strip().upper()

                gender= 'MALE' if gender == 'M' else 'FEMALE' if gender == 'F' else 'OTHER'

                # Get Triggers and Hygine checks...
                if voter_front_img != None :
                    print("voter_back_img",voter_back_img)
                    VOTER_ID_T_H = {}
                    VOTER_ID_T_H = VOTER_ID_TH(
                    Name                = { "FORM": (user_name+" "+user_last_name).strip(), "SERVICE": VOTER_ID_RESULT["Name_of_the_card_holder"].encode("ascii", "ignore").decode().replace("(","").replace(")","").replace(",","").strip().upper() }, 
                    FathersName         = { "FORM": fathers_name,    "SERVICE": VOTER_ID_RESULT["Name_of_relative"].encode("ascii", "ignore").decode().replace("(","").replace(")","").replace(",","").strip().upper() }, 
                    DOB                 = { "FORM": dob },
                    gender              = { "FORM": gender,          "SERVICE":VOTER_ID_RESULT["Card_holders_gender"].strip().upper()}, 
                    voterid             = { "FORM": epic_no.upper(), "SERVICE": VOTER_ID_RESULT["EPIC_Voter_ID_Number"].strip().upper() }, 
                    pin                 = { "FORM": pin }, 
                    city                = { "FORM": city,            "SERVICE": VOTER_ID_RESULT["Parliamentary_Constituency_applicable_to_the_card_holder"].encode("ascii", "ignore").decode().replace("(","").replace(")","").replace(",","").strip().upper() }, 
                    state               = { "FORM": state,           "SERVICE": VOTER_ID_RESULT["State_of_the_registered_Electoral_Office"].strip().upper() }, 
                    address             = { "FORM": address,         "SERVICE":(VOTER_ID_RESULT["Assembly_Constituency_applicable_to_the_card_holder"].encode("ascii", "ignore").decode().replace("(","").replace(")","").replace(",","").strip() +" "+VOTER_ID_RESULT["Constituency_applicable_to_the_card_holder"].encode("ascii", "ignore").decode().replace("(","").replace(")","").replace(",","").strip() +" "+VOTER_ID_RESULT["District_of_the_Electoral_Office"].encode("ascii", "ignore").decode().replace("(","").replace(")","").replace(",","").strip()).upper() },
                    image_base64_front  = voter_front_img,
                    image_base64_back   = voter_back_img if voter_back_img != None else ''
                        )
                    VOTER_ID_RESULT["T_H"] = VOTER_ID_T_H
        
    else:
        if not mode:
             application_meta.response_metadata = {}
        RESP_CODE = "500"
        
    billing_details = billable_and_response_msg(response_code=RESP_CODE)

    if not mode:
        application_meta.response_metadata["input_data"]              = {}
        application_meta.response_metadata["input_data"]["epic_no"]   = application_data.vid

        transaction = []

        if analysis_mode:
            transaction.append({
                            "api": "VOTER IDR",
                            "billable": billing_details["BILLABLE"],
                            "response_code": RESP_CODE,
                        })
        else:
            transaction.append({
                            "api": "VOTER_ID",
                            "billable": billing_details["BILLABLE"],
                            "response_code": RESP_CODE,
                        })
                
        transactions_log.objects.enter_trx_log(
            application_number = application_meta.application_number, 
            login_id           = application_meta.login_id, 
            product            = application_meta.product,
            state              = application_meta.state,
            transactions       = transaction, 
            transactions_type  = application_meta.transactions_type,
            response_metadata  = application_meta.response_metadata,
            request_id         = application_data.request_id if 'request_id' in application_data.keys() else '' 
        )

    return VOTER_ID_RESULT, billing_details["BILLABLE"], RESP_CODE, billing_details["MESSAGE"]