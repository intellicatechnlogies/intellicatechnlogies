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


#from core.components.API.clients.Email_send_dev import send_email_code_exception_record 

#rc_regex = compile_regex("[0-9]{1,2}[A-Za-z]{1,3}[0-9]{1,4}")

# def valid_RC_no(rc_number:str):
#     StateAbbr = ["AN","AP","AR","AS","BR","CH","CG","DN","DD","DL","GA","GJ","HR","HP","JK","JH","KA","KL","LA","LD","MP","MH","MN","ML","MZ","NL","OD","PY","PB","RJ","SK","TN","TS","TR","UP","UK","WB"]
#     rc_no = str(rc_number).strip().upper()
#     if len(rc_no) >= 5 and str(rc_no[:2]) in StateAbbr:
#         return True if validate_with_regex(rc_regex, rc_no[2:]) else False
#     return False

class RC:
    def __init__(self, mode="BULK", rc_no="",rec_id=None, meta_data=None):
        self.__rc_no = rc_no
        self.__mode = mode
        self.__result_dict = Munch()
        self.__response_metada = Munch()

        if self.__mode=="IDR":
            self.get_rc_results(rec_id=rec_id, meta_data=meta_data)
        if self.__mode=="BULK":
            self.get_bulk_rc_newurl_result()
        if self.__mode=="TEST":
            self.get_bulk_rc_test_result()

    def get_bulk_rc_newurl_result(self):
        self.__result_dict.name_of_the_owner                                  = ""
        self.__result_dict.fathers_name_of_the_owner                          = ""
        self.__result_dict.mobile_number                                      = ""
        self.__result_dict.serial_number_of_owner                             = ""
        self.__result_dict.current_address                                    = ""
        self.__result_dict.permanent_address                                  = ""
        self.__result_dict.name_of_insurance_company                          = ""
        self.__result_dict.insurance_policy_number_of_the_vehicle             = ""
        self.__result_dict.date_of_validity_of_rc_insurance                   = ""
        self.__result_dict.name_of_vehicles_financer                          = ""
        self.__result_dict.rc_blacklist_status                                = ""
        self.__result_dict.state_code                                         = ""
        self.__result_dict.rc_noc_details                                     = ""
        self.__result_dict.vehicle_registration_number                        = ""
        self.__result_dict.vehicle_registration_date                          = ""
        self.__result_dict.status_of_RC                                       = ""
        self.__result_dict.rc_mapper_class                                    = ""
        self.__result_dict.rc_commercial_status                               = ""
        self.__result_dict.rto_of_registration_of_the_vehicle                 = ""
        self.__result_dict.duration_till_the_tax_on_the_vehicle_has_been_paid = ""
        self.__result_dict.vehicle_category                                   = ""
        self.__result_dict.description_of_vehicles_class                      = ""
        self.__result_dict.chassis_number_of_the_vehicle                      = ""
        self.__result_dict.body_type_of_the_vehicle                           = ""
        self.__result_dict.vehicle_color                                      = ""
        self.__result_dict.cubic_capacity_of_the_vehicle_engine               = ""
        self.__result_dict.vehicle_norms                                      = ""
        self.__result_dict.vehicle_model_and_make                             = ""
        self.__result_dict.engine_number_of_the_vehicle                       = ""
        self.__result_dict.vehicle_fuel_type                                  = ""
        self.__result_dict.validity_of_vehicle_fitness                        = ""
        self.__result_dict.name_of_the_manufacturer                           = ""
        self.__result_dict.month_of_vehicle_manufacture                       = ""
        self.__result_dict.no_of_cylinders                                    = ""
        self.__result_dict.maximum_sleeper_cap                                = ""
        self.__result_dict.capacity_of_standing_passengers_in_the_vehicle     = ""
        self.__result_dict.vehicle_passenger_seating_capacity                 = ""
        self.__result_dict.gross_weight_of_the_vehicle                        = ""
        self.__result_dict.unladden_weight_of_the_vehicle                     = ""
        self.__result_dict.wheelbase_in_mm_of_the_vehicle                     = ""
        self.__result_dict.rc_pucc_no                                         = ""
        self.__result_dict.rc_pucc_upto                                       = ""
        self.__result_dict.date_of_rc_status_verification                     = ""
        self.__result_dict.response_code                                      = ""
        self.__result_dict.date_time                                          = ""
        self.__result_dict.response_message                                   = ""
        # base_url = config.zoop_base_url["base_url"]
        # url = f"{base_url}/in/vehicle/rc/advance"

        # payload = dump_as_JSON({
        #     "data": {
        #         "vehicle_registration_number": self.__rc_no,
        #         "consent": "Y",
        #         "consent_text": "RC Advance is Verified by author"
        #     }
        #     })
        # headers = {
        #         'api-key': config.zoop["api-key"],
        #         'app-id': config.zoop["app-id"],
        #         'Content-Type': 'application/json'
        #     }


        try:
            # response = make_HTTP_request("POST", url=url, data=payload, headers=headers, timeout=30)
            # api_response = response.json()
            # self.__response_metada = {key : value for key,value in api_response.items() if key != "result"}
            response=Much()
            response.status_code=200
            api_response=Munch()
            api_response={}
            api_response["response_code"]="100"
            if response.status_code == 200:
                if str(api_response["response_code"]) == "100":
                    self.__result_dict.response_code = "101"
                    #api_response_data = api_response["result"]
                    api_response_data={}
                    if "insurance" in api_response_data.keys():
                        insurance_data = api_response_data["insurance"]
                    else:
                        insurance_data = {}
                    self.__result_dict.body_type_of_the_vehicle                           = api_response_data["body_type_description"] if "body_type_description" in api_response_data.keys() and api_response_data["body_type_description"] != None else ""
                    self.__result_dict.capacity_of_standing_passengers_in_the_vehicle     = api_response_data["vehicle_stand_capacity"] if "vehicle_stand_capacity" in api_response_data.keys() and api_response_data["vehicle_stand_capacity"]  != None else ""
                    self.__result_dict.chassis_number_of_the_vehicle                      = api_response_data["rc_chassis_number"] if "rc_chassis_number" in api_response_data.keys() and api_response_data["rc_chassis_number"]  != None else ""
                    self.__result_dict.cubic_capacity_of_the_vehicle_engine               = api_response_data["vehicle_cubic_capacity"] if "vehicle_cubic_capacity" in api_response_data.keys() and api_response_data["vehicle_cubic_capacity"]  != None else ""
                    self.__result_dict.current_address                                    = api_response_data["user_present_address"] if "user_present_address" in api_response_data.keys() and api_response_data["user_present_address"]  != None else ""
                    self.__result_dict.date_of_rc_status_verification                     = api_response_data["rc_status_as_on"] if "rc_status_as_on" in api_response_data.keys() and api_response_data["rc_status_as_on"]  != None else ""
                    self.__result_dict.date_of_validity_of_rc_insurance                   = insurance_data["expiry_date"] if "expiry_date" in insurance_data.keys() and insurance_data["expiry_date"] != None else ""
                    self.__result_dict.description_of_vehicles_class                      = api_response_data["vehicle_class_description"] if "vehicle_class_description" in api_response_data.keys() and api_response_data["vehicle_class_description"]  != None else ""
                    self.__result_dict.duration_till_the_tax_on_the_vehicle_has_been_paid = api_response_data["rc_tax_upto"] if "rc_tax_upto" in api_response_data.keys() and api_response_data["rc_tax_upto"]  != None else ""
                    self.__result_dict.engine_number_of_the_vehicle                       = api_response_data["rc_engine_number"] if "rc_engine_number" in api_response_data.keys() and api_response_data["rc_engine_number"]  != None else ""
                    self.__result_dict.fathers_name_of_the_owner                          = api_response_data["father_name"] if "father_name" in api_response_data.keys() and api_response_data["father_name"]  != None else ""
                    self.__result_dict.gross_weight_of_the_vehicle                        = api_response_data["vehicle_gross_weight"] if "vehicle_gross_weight" in api_response_data.keys() and api_response_data["vehicle_gross_weight"]  != None else ""
                    self.__result_dict.insurance_policy_number_of_the_vehicle             = insurance_data["policy_number"] if "policy_number" in insurance_data.keys() and insurance_data["policy_number"]  != None else ""
                    self.__result_dict.maximum_sleeper_cap                                = api_response_data["vehicle_sleeper_capacity"] if "vehicle_sleeper_capacity" in api_response_data.keys() and api_response_data["vehicle_sleeper_capacity"]  != None else ""
                    self.__result_dict.mobile_number                                      = api_response_data["rc_mobile_no"] if "rc_mobile_no" in api_response_data.keys() and api_response_data["rc_mobile_no"]  != None else ""
                    self.__result_dict.month_of_vehicle_manufacture                       = api_response_data["vehicle_manufactured_date"] if "vehicle_manufactured_date" in api_response_data.keys() and api_response_data["vehicle_manufactured_date"]  != None else ""
                    self.__result_dict.name_of_insurance_company                          = insurance_data["company"] if "company" in insurance_data.keys() and insurance_data["company"]  != None else ""
                    self.__result_dict.name_of_the_manufacturer                           = api_response_data["vehicle_maker_description"] if "vehicle_maker_description" in api_response_data.keys() and api_response_data["vehicle_maker_description"]  != None else ""
                    self.__result_dict.name_of_the_owner                                  = api_response_data["user_name"] if "user_name" in api_response_data.keys() and api_response_data["user_name"]  != None else ""
                    self.__result_dict.name_of_vehicles_financer                          = api_response_data["financer"] if "financer" in api_response_data.keys() and api_response_data["financer"]  != None else ""
                    self.__result_dict.no_of_cylinders                                    = api_response_data["vehicle_number_of_cylinders"] if "vehicle_number_of_cylinders" in api_response_data.keys() and api_response_data["vehicle_number_of_cylinders"]  != None else ""
                    self.__result_dict.permanent_address                                  = api_response_data["user_permanent_address"] if "user_permanent_address" in api_response_data.keys() and api_response_data["user_permanent_address"]  != None else ""
                    self.__result_dict.rc_mapper_class                                    = api_response_data["rc_mapper_class"] if "rc_mapper_class" in api_response_data.keys() and api_response_data["rc_mapper_class"] != None else ""
                    self.__result_dict.rc_commercial_status                               = api_response_data["rc_commercial_status"] if "rc_commercial_status" in api_response_data.keys() and api_response_data["rc_commercial_status"] != None else ""
                    self.__result_dict.rc_blacklist_status                                = api_response_data["rc_blacklist_status"] if "rc_blacklist_status" in api_response_data.keys() and api_response_data["rc_blacklist_status"]  != None else ""
                    self.__result_dict.rc_noc_details                                     = api_response_data["rc_noc_details"] if "rc_noc_details" in api_response_data.keys() and api_response_data["rc_noc_details"]  != None else ""
                    self.__result_dict.rc_pucc_no                                         = api_response_data["rc_pucc_no"] if "rc_pucc_no" in api_response_data.keys() and api_response_data["rc_pucc_no"]  != None else ""
                    self.__result_dict.rc_pucc_upto                                       = api_response_data["rc_pucc_expiry_date"] if "rc_pucc_expiry_date" in api_response_data.keys() and api_response_data["rc_pucc_expiry_date"]  != None else ""
                    self.__result_dict.rto_of_registration_of_the_vehicle                 = api_response_data["rc_registration_location"] if "rc_registration_location" in api_response_data.keys() and api_response_data["rc_registration_location"]  != None else ""
                    self.__result_dict.serial_number_of_owner                             = api_response_data["vehicle_owner_number"] if "vehicle_owner_number" in api_response_data.keys() and api_response_data["vehicle_owner_number"]  != None else ""
                    self.__result_dict.state_code                                         = api_response_data["rc_state_code"] if "rc_state_code" in api_response_data.keys() and api_response_data["rc_state_code"]  != None else ""
                    self.__result_dict.status_of_RC                                       = api_response_data["rc_status"] if "rc_status" in api_response_data.keys() and api_response_data["rc_status"]  != None else ""
                    self.__result_dict.unladden_weight_of_the_vehicle                     = api_response_data["vehicle_unladen_weight"] if "vehicle_unladen_weight" in api_response_data.keys() and api_response_data["vehicle_unladen_weight"]  != None else ""
                    self.__result_dict.validity_of_vehicle_fitness                        = api_response_data["rc_fit_upto"] if "rc_fit_upto" in api_response_data.keys() and api_response_data["rc_fit_upto"]  != None else ""
                    self.__result_dict.vehicle_category                                   = api_response_data["vehicle_category"] if "vehicle_category" in api_response_data.keys() and api_response_data["vehicle_category"]  != None else ""
                    self.__result_dict.vehicle_color                                      = api_response_data["vehicle_color"] if "vehicle_color" in api_response_data.keys() and api_response_data["vehicle_color"]  != None else ""
                    self.__result_dict.vehicle_fuel_type                                  = api_response_data["vehicle_fuel_description"] if "vehicle_fuel_description" in api_response_data.keys() and api_response_data["vehicle_fuel_description"]  != None else ""
                    self.__result_dict.vehicle_model_and_make                             = api_response_data["vehicle_make_model"] if "vehicle_make_model" in api_response_data.keys() and api_response_data["vehicle_make_model"]  != None else ""
                    self.__result_dict.vehicle_norms                                      = api_response_data["norms_description"] if "norms_description" in api_response_data.keys() and api_response_data["norms_description"]  != None else ""
                    self.__result_dict.vehicle_passenger_seating_capacity                 = api_response_data["vehicle_seating_capacity"] if "vehicle_seating_capacity" in api_response_data.keys() and api_response_data["vehicle_seating_capacity"]  != None else ""
                    self.__result_dict.vehicle_registration_date                          = api_response_data["rc_registration_date"] if "rc_registration_date" in api_response_data.keys() and api_response_data["rc_registration_date"]  != None else ""
                    self.__result_dict.vehicle_registration_number                        = api_response_data["rc_registration_number"] if "rc_registration_number" in api_response_data.keys() and api_response_data["rc_registration_number"]  != None else ""
                    self.__result_dict.wheelbase_in_mm_of_the_vehicle                     = api_response_data["vehicle_wheelbase"] if "vehicle_wheelbase" in api_response_data.keys() and api_response_data["vehicle_wheelbase"]  != None else ""
                elif str(api_response["response_code"]) in ("101","103"):
                    self.__result_dict.response_code = "103"
                elif str(api_response["response_code"]) == "102":
                    self.__result_dict.response_code = "106"
                    metadata = api_response["metadata"]
                    self.__result_dict.response_message = metadata["reason_message"] if "reason_message" in metadata and metadata["reason_message"] not in ["", "NA"] else "" 
                else:
                    self.__result_dict.response_code = "500"
            elif response.status_code == 400:
                if str(api_response["response_code"]) == "106":
                    self.__result_dict.response_code = "102"
                elif str(api_response["response_code"]) == "105":
                    self.__result_dict.response_code = "104"
                elif str(api_response["response_code"]) == "104":
                    self.__result_dict.response_code = "105"
                else:
                    self.__result_dict.response_code = "500"
            elif response.status_code in [500,503,504]:
                self.__result_dict.response_code = "110"
            else:
                self.__result_dict.response_code = "500"
        except Exception as ex:
            self.__result_dict.response_code = "510"

        self.__result_dict.date_time = str(dt.now().strftime("%Y-%m-%d %H:%M:%S"))


    # def get_bulk_rc_test_result(self):
    #     self.__result_dict.name_of_the_owner                                  = ""
    #     self.__result_dict.fathers_name_of_the_owner                          = ""
    #     self.__result_dict.mobile_number                                      = ""
    #     self.__result_dict.serial_number_of_owner                             = ""
    #     self.__result_dict.current_address                                    = ""
    #     self.__result_dict.permanent_address                                  = ""
    #     self.__result_dict.name_of_insurance_company                          = ""
    #     self.__result_dict.insurance_policy_number_of_the_vehicle             = ""
    #     self.__result_dict.date_of_validity_of_rc_insurance                   = ""
    #     self.__result_dict.name_of_vehicles_financer                          = ""
    #     self.__result_dict.rc_blacklist_status                                = ""
    #     self.__result_dict.state_code                                         = ""
    #     self.__result_dict.rc_noc_details                                     = ""
    #     self.__result_dict.vehicle_registration_number                        = ""
    #     self.__result_dict.vehicle_registration_date                          = ""
    #     self.__result_dict.status_of_RC                                       = ""
    #     self.__result_dict.rc_mapper_class                                    = ""
    #     self.__result_dict.rc_commercial_status                               = ""
    #     self.__result_dict.rto_of_registration_of_the_vehicle                 = ""
    #     self.__result_dict.duration_till_the_tax_on_the_vehicle_has_been_paid = ""
    #     self.__result_dict.vehicle_category                                   = ""
    #     self.__result_dict.description_of_vehicles_class                      = ""
    #     self.__result_dict.chassis_number_of_the_vehicle                      = ""
    #     self.__result_dict.body_type_of_the_vehicle                           = ""
    #     self.__result_dict.vehicle_color                                      = ""
    #     self.__result_dict.cubic_capacity_of_the_vehicle_engine               = ""
    #     self.__result_dict.vehicle_norms                                      = ""
    #     self.__result_dict.vehicle_model_and_make                             = ""
    #     self.__result_dict.engine_number_of_the_vehicle                       = ""
    #     self.__result_dict.vehicle_fuel_type                                  = ""
    #     self.__result_dict.validity_of_vehicle_fitness                        = ""
    #     self.__result_dict.name_of_the_manufacturer                           = ""
    #     self.__result_dict.month_of_vehicle_manufacture                       = ""
    #     self.__result_dict.no_of_cylinders                                    = ""
    #     self.__result_dict.maximum_sleeper_cap                                = ""
    #     self.__result_dict.capacity_of_standing_passengers_in_the_vehicle     = ""
    #     self.__result_dict.vehicle_passenger_seating_capacity                 = ""
    #     self.__result_dict.gross_weight_of_the_vehicle                        = ""
    #     self.__result_dict.unladden_weight_of_the_vehicle                     = ""
    #     self.__result_dict.wheelbase_in_mm_of_the_vehicle                     = ""
    #     self.__result_dict.rc_pucc_no                                         = ""
    #     self.__result_dict.rc_pucc_upto                                       = ""
    #     self.__result_dict.date_of_rc_status_verification                     = ""
    #     self.__result_dict.response_code                                      = ""
    #     self.__result_dict.date_time                                          = ""
    #     self.__result_dict.response_message                                   = ""
    #     base_url = config.zoop_test_url["base_url"]
    #     url = f"{base_url}/in/vehicle/rc/advance"

    #     payload = dump_as_JSON({
    #         "data": {
    #             "vehicle_registration_number": self.__rc_no,
    #             "consent": "Y",
    #             "consent_text": "RC Advance is Verified by author"
    #         }
    #         })
    #     headers = {
    #             'api-key': config.zoop_test["api-key"],
    #             'app-id': config.zoop_test["app-id"],
    #             'Content-Type': 'application/json'
    #         }

    #     try:
    #         response = make_HTTP_request("POST", url=url, data=payload, headers=headers, timeout=30)
    #         api_response = response.json()
    #         self.__response_metada = {key : value for key,value in api_response.items() if key != "result"}
    #         if str(response.status_code) == "200":
    #             if str(api_response["response_code"]) == "100":
    #                 self.__result_dict.response_code = "101"
    #                 api_response_data = api_response["result"]
    #                 if "insurance" in api_response_data.keys():
    #                     insurance_data = api_response_data["insurance"]
    #                 else:
    #                     insurance_data = {}
    #                 self.__result_dict.body_type_of_the_vehicle                           = api_response_data["body_type_description"] if "body_type_description" in api_response_data.keys() and api_response_data["body_type_description"] != None else ""
    #                 self.__result_dict.capacity_of_standing_passengers_in_the_vehicle     = api_response_data["vehicle_stand_capacity"] if "vehicle_stand_capacity" in api_response_data.keys() and api_response_data["vehicle_stand_capacity"]  != None else ""
    #                 self.__result_dict.chassis_number_of_the_vehicle                      = api_response_data["rc_chassis_number"] if "rc_chassis_number" in api_response_data.keys() and api_response_data["rc_chassis_number"]  != None else ""
    #                 self.__result_dict.cubic_capacity_of_the_vehicle_engine               = api_response_data["vehicle_cubic_capacity"] if "vehicle_cubic_capacity" in api_response_data.keys() and api_response_data["vehicle_cubic_capacity"]  != None else ""
    #                 self.__result_dict.current_address                                    = api_response_data["user_present_address"] if "user_present_address" in api_response_data.keys() and api_response_data["user_present_address"]  != None else ""
    #                 self.__result_dict.date_of_rc_status_verification                     = api_response_data["rc_status_as_on"] if "rc_status_as_on" in api_response_data.keys() and api_response_data["rc_status_as_on"]  != None else ""
    #                 self.__result_dict.date_of_validity_of_rc_insurance                   = insurance_data["expiry_date"] if "expiry_date" in insurance_data.keys() and insurance_data["expiry_date"] != None else ""
    #                 self.__result_dict.description_of_vehicles_class                      = api_response_data["vehicle_class_description"] if "vehicle_class_description" in api_response_data.keys() and api_response_data["vehicle_class_description"]  != None else ""
    #                 self.__result_dict.duration_till_the_tax_on_the_vehicle_has_been_paid = api_response_data["rc_tax_upto"] if "rc_tax_upto" in api_response_data.keys() and api_response_data["rc_tax_upto"]  != None else ""
    #                 self.__result_dict.engine_number_of_the_vehicle                       = api_response_data["rc_engine_number"] if "rc_engine_number" in api_response_data.keys() and api_response_data["rc_engine_number"]  != None else ""
    #                 self.__result_dict.fathers_name_of_the_owner                          = api_response_data["father_name"] if "father_name" in api_response_data.keys() and api_response_data["father_name"]  != None else ""
    #                 self.__result_dict.gross_weight_of_the_vehicle                        = api_response_data["vehicle_gross_weight"] if "vehicle_gross_weight" in api_response_data.keys() and api_response_data["vehicle_gross_weight"]  != None else ""
    #                 self.__result_dict.insurance_policy_number_of_the_vehicle             = insurance_data["policy_number"] if "policy_number" in insurance_data.keys() and insurance_data["policy_number"]  != None else ""
    #                 self.__result_dict.maximum_sleeper_cap                                = api_response_data["vehicle_sleeper_capacity"] if "vehicle_sleeper_capacity" in api_response_data.keys() and api_response_data["vehicle_sleeper_capacity"]  != None else ""
    #                 self.__result_dict.mobile_number                                      = api_response_data["rc_mobile_no"] if "rc_mobile_no" in api_response_data.keys() and api_response_data["rc_mobile_no"]  != None else ""
    #                 self.__result_dict.month_of_vehicle_manufacture                       = api_response_data["vehicle_manufactured_date"] if "vehicle_manufactured_date" in api_response_data.keys() and api_response_data["vehicle_manufactured_date"]  != None else ""
    #                 self.__result_dict.name_of_insurance_company                          = insurance_data["company"] if "company" in insurance_data.keys() and insurance_data["company"]  != None else ""
    #                 self.__result_dict.name_of_the_manufacturer                           = api_response_data["vehicle_maker_description"] if "vehicle_maker_description" in api_response_data.keys() and api_response_data["vehicle_maker_description"]  != None else ""
    #                 self.__result_dict.name_of_the_owner                                  = api_response_data["user_name"] if "user_name" in api_response_data.keys() and api_response_data["user_name"]  != None else ""
    #                 self.__result_dict.name_of_vehicles_financer                          = api_response_data["financer"] if "financer" in api_response_data.keys() and api_response_data["financer"]  != None else ""
    #                 self.__result_dict.no_of_cylinders                                    = api_response_data["vehicle_number_of_cylinders"] if "vehicle_number_of_cylinders" in api_response_data.keys() and api_response_data["vehicle_number_of_cylinders"]  != None else ""
    #                 self.__result_dict.permanent_address                                  = api_response_data["user_permanent_address"] if "user_permanent_address" in api_response_data.keys() and api_response_data["user_permanent_address"]  != None else ""
    #                 self.__result_dict.rc_mapper_class                                    = api_response_data["rc_mapper_class"] if "rc_mapper_class" in api_response_data.keys() and api_response_data["rc_mapper_class"] != None else ""
    #                 self.__result_dict.rc_commercial_status                               = api_response_data["rc_commercial_status"] if "rc_commercial_status" in api_response_data.keys() and api_response_data["rc_commercial_status"] != None else ""
    #                 self.__result_dict.rc_blacklist_status                                = api_response_data["rc_blacklist_status"] if "rc_blacklist_status" in api_response_data.keys() and api_response_data["rc_blacklist_status"]  != None else ""
    #                 self.__result_dict.rc_noc_details                                     = api_response_data["rc_noc_details"] if "rc_noc_details" in api_response_data.keys() and api_response_data["rc_noc_details"]  != None else ""
    #                 self.__result_dict.rc_pucc_no                                         = api_response_data["rc_pucc_no"] if "rc_pucc_no" in api_response_data.keys() and api_response_data["rc_pucc_no"]  != None else ""
    #                 self.__result_dict.rc_pucc_upto                                       = api_response_data["rc_pucc_expiry_date"] if "rc_pucc_expiry_date" in api_response_data.keys() and api_response_data["rc_pucc_expiry_date"]  != None else ""
    #                 self.__result_dict.rto_of_registration_of_the_vehicle                 = api_response_data["rc_registration_location"] if "rc_registration_location" in api_response_data.keys() and api_response_data["rc_registration_location"]  != None else ""
    #                 self.__result_dict.serial_number_of_owner                             = api_response_data["vehicle_owner_number"] if "vehicle_owner_number" in api_response_data.keys() and api_response_data["vehicle_owner_number"]  != None else ""
    #                 self.__result_dict.state_code                                         = api_response_data["rc_state_code"] if "rc_state_code" in api_response_data.keys() and api_response_data["rc_state_code"]  != None else ""
    #                 self.__result_dict.status_of_RC                                       = api_response_data["rc_status"] if "rc_status" in api_response_data.keys() and api_response_data["rc_status"]  != None else ""
    #                 self.__result_dict.unladden_weight_of_the_vehicle                     = api_response_data["vehicle_unladen_weight"] if "vehicle_unladen_weight" in api_response_data.keys() and api_response_data["vehicle_unladen_weight"]  != None else ""
    #                 self.__result_dict.validity_of_vehicle_fitness                        = api_response_data["rc_fit_upto"] if "rc_fit_upto" in api_response_data.keys() and api_response_data["rc_fit_upto"]  != None else ""
    #                 self.__result_dict.vehicle_category                                   = api_response_data["vehicle_category"] if "vehicle_category" in api_response_data.keys() and api_response_data["vehicle_category"]  != None else ""
    #                 self.__result_dict.vehicle_color                                      = api_response_data["vehicle_color"] if "vehicle_color" in api_response_data.keys() and api_response_data["vehicle_color"]  != None else ""
    #                 self.__result_dict.vehicle_fuel_type                                  = api_response_data["vehicle_fuel_description"] if "vehicle_fuel_description" in api_response_data.keys() and api_response_data["vehicle_fuel_description"]  != None else ""
    #                 self.__result_dict.vehicle_model_and_make                             = api_response_data["vehicle_make_model"] if "vehicle_make_model" in api_response_data.keys() and api_response_data["vehicle_make_model"]  != None else ""
    #                 self.__result_dict.vehicle_norms                                      = api_response_data["norms_description"] if "norms_description" in api_response_data.keys() and api_response_data["norms_description"]  != None else ""
    #                 self.__result_dict.vehicle_passenger_seating_capacity                 = api_response_data["vehicle_seating_capacity"] if "vehicle_seating_capacity" in api_response_data.keys() and api_response_data["vehicle_seating_capacity"]  != None else ""
    #                 self.__result_dict.vehicle_registration_date                          = api_response_data["rc_registration_date"] if "rc_registration_date" in api_response_data.keys() and api_response_data["rc_registration_date"]  != None else ""
    #                 self.__result_dict.vehicle_registration_number                        = api_response_data["rc_registration_number"] if "rc_registration_number" in api_response_data.keys() and api_response_data["rc_registration_number"]  != None else ""
    #                 self.__result_dict.wheelbase_in_mm_of_the_vehicle                     = api_response_data["vehicle_wheelbase"] if "vehicle_wheelbase" in api_response_data.keys() and api_response_data["vehicle_wheelbase"]  != None else ""
    #             elif str(api_response["response_code"]) in ("101","103"):
    #                 self.__result_dict.response_code = "103"
    #             elif str(api_response["response_code"]) == "102":
    #                 self.__result_dict.response_code = "106"
    #                 metadata = api_response["metadata"]
    #                 self.__result_dict.response_message = metadata["reason_message"] if "reason_message" in metadata and metadata["reason_message"] not in ["", "NA"] else "" 
    #             else:
    #                 self.__result_dict.response_code = "500"
    #         elif str(response.status_code) == "400":
    #             if str(api_response["response_code"]) == "106":
    #                 self.__result_dict.response_code = "102"
    #             elif str(api_response["response_code"]) == "105":
    #                 self.__result_dict.response_code = "104"
    #             elif str(api_response["response_code"]) == "104":
    #                 self.__result_dict.response_code = "105"
    #             else:
    #                 self.__result_dict.response_code = "500"
    #         elif str(response.status_code) in ["500","503","504"]:
    #             self.__result_dict.response_code = "110"
    #         else:
    #             self.__result_dict.response_code = "500"
    #     except Exception as ex:
    #         self.__result_dict.response_code = "510"

    #     self.__result_dict.date_time = str(dt.now().strftime("%Y-%m-%d %H:%M:%S"))


    def get_rc_results(self,rec_id, meta_data):
        # ADDRESS DETAILS
        self.__result_dict.address                          = Munch()
        self.__result_dict.address.present                  = "NA"
        self.__result_dict.address.permanent                = "NA"
        self.__result_dict.address.pin_code                 = "NA"
        # FINANCE DETAILS
        self.__result_dict.finance                          = Munch()
        self.__result_dict.finance.financer                 = "NA"
        self.__result_dict.finance.rc_financed_from         = "NA"
        # INSURANCE DETAILS
        self.__result_dict.insurance                        = Munch()
        self.__result_dict.insurance.company                = "NA"
        self.__result_dict.insurance.policy_num             = "NA"
        self.__result_dict.insurance.valid_upto             = "NA"
        # LEGAL RC DETAILS
        self.__result_dict.legal                            = Munch()
        self.__result_dict.legal.blacklist                  = "NA"
        self.__result_dict.legal.expiry_date                = "NA"
        self.__result_dict.legal.noc                        = "NA"
        self.__result_dict.legal.rc_number                  = "NA"
        self.__result_dict.legal.registration_date          = "NA"
        self.__result_dict.legal.rc_registered_at           = "NA"
        self.__result_dict.legal.rc_status                  = "NA"
        self.__result_dict.legal.rc_status_as_on            = "NA"
        self.__result_dict.legal.state_cd                   = "NA"
        self.__result_dict.legal.statusMessage              = "NA"
        self.__result_dict.legal.tax_upto_date              = "NA"
        self.__result_dict.legal.rc_is_commercial           = "NA"
        self.__result_dict.legal.rc_non_use_from            = "NA"
        self.__result_dict.legal.rc_non_use_status          = "NA"
        self.__result_dict.legal.rc_non_use_to              = "NA"
        self.__result_dict.legal.rc_np_issued_by            = "NA"
        self.__result_dict.legal.rc_np_no                   = "NA"
        self.__result_dict.legal.rc_np_upto                 = "NA"
        self.__result_dict.legal.rc_permit_issue_dt         = "NA"
        self.__result_dict.legal.rc_permit_no               = "NA"
        self.__result_dict.legal.rc_permit_type             = "NA"
        self.__result_dict.legal.rc_permit_valid_from       = "NA"
        self.__result_dict.legal.rc_permit_valid_upto       = "NA"
        self.__result_dict.legal.rc_source                  = "NA"
        self.__result_dict.legal.rc_mapper_class            = "NA"
        # OWNER DETAILS
        self.__result_dict.owner                            = Munch()
        self.__result_dict.owner.father_husband             = "NA"
        self.__result_dict.owner.name                       = "NA"
        self.__result_dict.owner.rc_mobile_no               = "NA"
        self.__result_dict.owner.rc_owner_first_name        = "NA"
        self.__result_dict.owner.rc_owner_second_name       = "NA"
        self.__result_dict.owner.rc_owner_sr                = "NA"
        # POLLUTION DETAILS
        self.__result_dict.polution                         = Munch()
        self.__result_dict.polution.number                  = "NA"
        self.__result_dict.polution.valid_upto              = "NA"
        # VEHICLE DETAILS
        self.__result_dict.vehicle                          = Munch()
        self.__result_dict.vehicle.category                 = "NA"
        self.__result_dict.vehicle.chesis_number            = "NA"
        self.__result_dict.vehicle.color                    = "NA"
        self.__result_dict.vehicle.rc_body_type_desc        = "NA"
        self.__result_dict.vehicle.cubic_cap                = "NA"
        self.__result_dict.vehicle.emmission_std            = "NA"
        self.__result_dict.vehicle.engine                   = "NA"
        self.__result_dict.vehicle.fuel                     = "NA"
        self.__result_dict.vehicle.MMV                      = "NA"
        self.__result_dict.vehicle.manufacturer             = "NA"
        self.__result_dict.vehicle.manufacture_on           = "NA"
        self.__result_dict.vehicle.no_cyl                   = "NA"
        self.__result_dict.vehicle.seat_cap                 = "NA"
        self.__result_dict.vehicle.weight_gross             = "NA"
        self.__result_dict.vehicle.weight_unldn             = "NA"
        self.__result_dict.vehicle.rc_sleeper_cap           = "NA"
        self.__result_dict.vehicle.rc_stand_cap             = "NA"
        self.__result_dict.vehicle.rc_vch_catg              = "NA"
        self.__result_dict.vehicle.rc_vch_catg_desc         = "NA"
        self.__result_dict.vehicle.rc_vehicle_type          = "NA"
        self.__result_dict.vehicle.rc_vhc_class_cd          = "NA"
        self.__result_dict.vehicle.rc_vhc_class_type        = "NA"
        self.__result_dict.vehicle.wheelbase                = "NA"
        self.__result_dict.rc_no                            = self.__rc_no
        self.__result_dict.response_code                    = "110"
        
        try:
            base_url = config.zoop_base_url["base_url"]
            url = f"{base_url}/in/vehicle/rc/advance"

            payload = dump_as_JSON({
                "data": {
                    "vehicle_registration_number": self.__rc_no,
                    "consent": "Y",
                    "consent_text": "RC Advance is Verified by author"
                }
                })
            headers = {
                    'api-key': config.zoop["api-key"],
                    'app-id': config.zoop["app-id"],
                    'Content-Type': 'application/json'
                }

            response = make_HTTP_request("POST", url=url, data=payload, headers=headers, timeout=30)
            api_response = response.json()
            self.__response_metada = {key : value for key,value in api_response.items() if key != "result"}
            if str(response.status_code) == "200":
                if str(api_response["response_code"]) == "100":
                    self.__result_dict.response_code = "101"
                    api_response_data = api_response["result"]
                    api_response_keys = list(api_response_data.keys())
                    if "insurance" in api_response_keys:
                        insurance_data = api_response_data["insurance"]
                    else:
                        insurance_data = {}
                    # ADDRESS DETAILS
                    self.__result_dict.address.present         = api_response_data["user_present_address"] if "user_present_address" in api_response_data.keys() and api_response_data["user_present_address"]  != None else ""
                    self.__result_dict.address.permanent       = api_response_data["user_permanent_address"] if "user_permanent_address" in api_response_data.keys() and api_response_data["user_permanent_address"]  != None else ""
                    
                    # FINANCE DETAILS
                    self.__result_dict.finance.financer         = api_response_data["financer"] if "financer" in api_response_data.keys() and api_response_data["financer"] != None else ""
                    
                    # INSURANCE DETAILS
                    self.__result_dict.insurance.company       = insurance_data["company"] if "company" in insurance_data.keys() and insurance_data["company"]  != None else ""
                    self.__result_dict.insurance.policy_num    = insurance_data["policy_number"] if "policy_number" in insurance_data.keys() and insurance_data["policy_number"]  != None else ""
                    self.__result_dict.insurance.valid_upto    = insurance_data["expiry_date"] if "expiry_date" in insurance_data.keys() and insurance_data["expiry_date"] != None else ""
                    # LEGAL RC DETAILS
                    self.__result_dict.legal.blacklist             = api_response_data["rc_blacklist_status"] if "rc_blacklist_status" in api_response_data.keys() and api_response_data["rc_blacklist_status"]  != None else ""
                    self.__result_dict.legal.expiry_date           = api_response_data["rc_fit_upto"] if "rc_fit_upto" in api_response_data.keys() and api_response_data["rc_fit_upto"]  != None else ""
                    self.__result_dict.legal.noc                   = api_response_data["rc_noc_details"] if "rc_noc_details" in api_response_data.keys() and api_response_data["rc_noc_details"]  != None else ""
                    self.__result_dict.legal.rc_number             = api_response_data["rc_registration_number"] if "rc_registration_number" in api_response_data.keys() and api_response_data["rc_registration_number"]  != None else ""
                    self.__result_dict.legal.registration_date     = api_response_data["rc_registration_date"] if "rc_registration_date" in api_response_data.keys() and api_response_data["rc_registration_date"]  != None else ""
                    self.__result_dict.legal.tax_upto_date         = api_response_data["rc_tax_upto"] if "rc_tax_upto" in api_response_data.keys() and api_response_data["rc_tax_upto"]  != None else ""
                    self.__result_dict.legal.rc_registered_at      = api_response_data["rc_registration_location"] if "rc_registration_location" in api_response_data.keys() and api_response_data["rc_registration_location"]  != None else ""
                    self.__result_dict.legal.rc_status             = api_response_data["rc_status"] if "rc_status" in api_response_data.keys() and api_response_data["rc_status"]  != None else ""
                    self.__result_dict.legal.rc_status_as_on       = api_response_data["rc_status_as_on"] if "rc_status_as_on" in api_response_data.keys() and api_response_data["rc_status_as_on"]  != None else ""
                    self.__result_dict.legal.state_cd              = api_response_data["rc_state_code"] if "rc_state_code" in api_response_data.keys() and api_response_data["rc_state_code"]  != None else ""
                    self.__result_dict.legal.rc_mapper_class       = api_response_data["rc_mapper_class"] if "rc_mapper_class" in api_response_data.keys() and api_response_data["rc_mapper_class"] != None else ""
                    # OWNER DETAILS
                    self.__result_dict.owner.father_husband        = api_response_data["father_name"] if "father_name" in api_response_data.keys() and api_response_data["father_name"]  != None else ""
                    self.__result_dict.owner.name                  = api_response_data["user_name"] if "user_name" in api_response_data.keys() and api_response_data["user_name"]  != None else ""
                    self.__result_dict.owner.rc_mobile_no          = api_response_data["rc_mobile_no"] if "rc_mobile_no" in api_response_data.keys() and api_response_data["rc_mobile_no"]  != None else ""
                    self.__result_dict.owner.rc_owner_sr           = api_response_data["vehicle_owner_number"] if "vehicle_owner_number" in api_response_data.keys() and api_response_data["vehicle_owner_number"]  != None else ""
                    # POLLUTION DETAILS
                    self.__result_dict.polution.number              = api_response_data["rc_pucc_no"] if "rc_pucc_no" in api_response_data.keys() and api_response_data["rc_pucc_no"]  != None else ""
                    self.__result_dict.polution.valid_upto          = api_response_data["rc_pucc_expiry_date"] if "rc_pucc_expiry_date" in api_response_data.keys() and api_response_data["rc_pucc_expiry_date"]  != None else ""
                    # VEHICLE DETAILS
                    self.__result_dict.vehicle.category             = api_response_data["vehicle_category"] if "vehicle_category" in api_response_data.keys() and api_response_data["vehicle_category"]  != None else ""
                    self.__result_dict.vehicle.chesis_number        = api_response_data["rc_chassis_number"] if "rc_chassis_number" in api_response_data.keys() and api_response_data["rc_chassis_number"]  != None else ""
                    self.__result_dict.vehicle.color                = api_response_data["vehicle_color"] if "vehicle_color" in api_response_data.keys() and api_response_data["vehicle_color"]  != None else ""
                    self.__result_dict.vehicle.rc_body_type_desc    = api_response_data["body_type_description"] if "body_type_description" in api_response_data.keys() and api_response_data["body_type_description"] != None else ""
                    self.__result_dict.vehicle.cubic_cap            = api_response_data["vehicle_cubic_capacity"] if "vehicle_cubic_capacity" in api_response_data.keys() and api_response_data["vehicle_cubic_capacity"]  != None else ""
                    self.__result_dict.vehicle.emmission_std        = api_response_data["norms_description"] if "norms_description" in api_response_data.keys() and api_response_data["norms_description"]  != None else ""
                    self.__result_dict.vehicle.engine               = api_response_data["rc_engine_number"] if "rc_engine_number" in api_response_data.keys() and api_response_data["rc_engine_number"]  != None else ""
                    self.__result_dict.vehicle.fuel                 = api_response_data["vehicle_fuel_description"] if "vehicle_fuel_description" in api_response_data.keys() and api_response_data["vehicle_fuel_description"]  != None else ""
                    self.__result_dict.vehicle.MMV                  = api_response_data["vehicle_maker_description"] if "vehicle_maker_description" in api_response_data.keys() and api_response_data["vehicle_maker_description"]  != None else ""
                    self.__result_dict.vehicle.manufacturer         = api_response_data["vehicle_maker_description"] if "vehicle_maker_description" in api_response_data.keys() and api_response_data["vehicle_maker_description"]  != None else ""
                    self.__result_dict.vehicle.manufacture_on       = api_response_data["vehicle_manufactured_date"] if "vehicle_manufactured_date" in api_response_data.keys() and api_response_data["vehicle_manufactured_date"]  != None else ""
                    self.__result_dict.vehicle.no_cyl               = api_response_data["vehicle_number_of_cylinders"] if "vehicle_number_of_cylinders" in api_response_data.keys() and api_response_data["vehicle_number_of_cylinders"]  != None else ""
                    self.__result_dict.vehicle.seat_cap             = api_response_data["vehicle_seating_capacity"] if "vehicle_seating_capacity" in api_response_data.keys() and api_response_data["vehicle_seating_capacity"]  != None else ""
                    self.__result_dict.vehicle.weight_gross         = api_response_data["vehicle_gross_weight"] if "vehicle_gross_weight" in api_response_data.keys() and api_response_data["vehicle_gross_weight"]  != None else ""
                    self.__result_dict.vehicle.weight_unldn         = api_response_data["vehicle_unladen_weight"] if "vehicle_unladen_weight" in api_response_data.keys() and api_response_data["vehicle_unladen_weight"]  != None else ""
                    self.__result_dict.vehicle.rc_sleeper_cap       = api_response_data["vehicle_sleeper_capacity"] if "vehicle_sleeper_capacity" in api_response_data.keys() and api_response_data["vehicle_sleeper_capacity"]  != None else ""
                    self.__result_dict.vehicle.rc_stand_cap         = api_response_data["vehicle_stand_capacity"] if "vehicle_stand_capacity" in api_response_data.keys() and api_response_data["vehicle_stand_capacity"]  != None else ""
                    self.__result_dict.vehicle.rc_vch_catg          = api_response_data["rc_vch_catg"]            if ("rc_vch_catg" in api_response_keys and str(api_response_data["rc_vch_catg"]).strip().upper() not in ["", "NONE", "NA"]) else "NA"
                    self.__result_dict.vehicle.rc_vch_catg_desc     = api_response_data["rc_vch_catg_desc"]        if ("rc_vch_catg_desc" in api_response_keys and str(api_response_data["rc_vch_catg_desc"]).strip().upper() not in ["", "NONE", "NA"]) else "NA"
                    self.__result_dict.vehicle.rc_vehicle_type      = api_response_data["rc_vehicle_type"]        if ("rc_vehicle_type" in api_response_keys and str(api_response_data["rc_vehicle_type"]).strip().upper() not in ["", "NONE", "NA"]) else "NA"
                    self.__result_dict.vehicle.rc_vhc_class_cd      = api_response_data["rc_vh_class_cd"]         if ("rc_vh_class_cd" in api_response_keys and str(api_response_data["rc_vh_class_cd"]).strip().upper() not in ["", "NONE", "NA"]) else "NA"
                    self.__result_dict.vehicle.rc_vhc_class_type    = api_response_data["rc_vhc_class_type"]      if ("rc_vhc_class_type" in api_response_keys and str(api_response_data["rc_vhc_class_type"]).strip().upper() not in ["", "NONE", "NA"]) else "NA"
                    self.__result_dict.vehicle.wheelbase            = api_response_data["vehicle_wheelbase"] if "vehicle_wheelbase" in api_response_data.keys() and api_response_data["vehicle_wheelbase"]  != None else ""
                elif str(api_response["response_code"]) in ("101","102","103"):
                    self.__result_dict.response_code = "103"
                else:
                    self.__result_dict.response_code = "500"
            elif str(response.status_code) == "400":
                if str(api_response["response_code"]) == "106":
                    self.__result_dict.response_code = "102"
                elif str(api_response["response_code"]) == "105":
                    self.__result_dict.response_code = "104"
                elif str(api_response["response_code"]) == "104":
                    self.__result_dict.response_code = "105"
                else:
                    self.__result_dict.response_code = "500"
            elif str(response.status_code) in ["500","503","504"]:
                self.__result_dict.response_code = "110"
            else:
                self.__result_dict.response_code = "110"
        except Exception as ex:
            self.__result_dict = Munch(map(lambda item: (item, '' if(item != 'rc_no') else self.__result_dict[item]), self.__result_dict.keys()))      
            self.__result_dict.response_code ="110"
            send_email_code_exception_record(api_response={"record_id":rec_id,"meta_data":meta_data,"error_code":f"exception of code {ex}"})
            print_debug_msg(f"Error occured due to {ex}") 
            

    @property
    def result(self):
        return self.__result_dict

    @property
    def metadata(self):
        return self.__response_metada

def rcCall(application_data: Munch=None, mode:str="BULK", application_meta: Munch=None, api_mode=False,record_id=None):
    rc_no = application_data.rc
    name  = application_data.name if 'name' in application_data.keys() else ''
    financer_name  = application_data.financer_name if 'financer_name' in application_data.keys() else ''
    if mode=="BULK":
        RC_INSTANCE = RC("BULK", rc_no)
    elif mode=="TEST":
        RC_INSTANCE = RC("TEST", rc_no)
    else:
        RC_INSTANCE = RC("IDR", rc_no,record_id, application_meta)

    RC_RESULT = RC_INSTANCE.result
    RC_RESULT.name_match="N/A"
    RC_RESULT.financer_match="N/A"
    billing_details = billable_and_response_msg(response_code=RC_RESULT.response_code if RC_RESULT.response_code else "500")
    if billing_details['BILLABLE']=='True':
       if 'name_of_the_owner' in RC_RESULT.keys() and len(str(RC_RESULT.name_of_the_owner).strip())>0 and len(name)>0:
            NAME_MATCH_PERCENTAGE_SERVICE = getMatchPercent(OCR_TEXT=name.upper(), ADDRESS_STR=RC_RESULT.name_of_the_owner.upper())
            if NAME_MATCH_PERCENTAGE_SERVICE == 100:
                NAME_MATCH_PERCENTAGE_SERVICE = getMatchPercent(OCR_TEXT=RC_RESULT.name_of_the_owner.upper(), ADDRESS_STR=name.upper())
                if NAME_MATCH_PERCENTAGE_SERVICE == 100:
                  RC_RESULT.name_match='Matched'
                else:
                 RC_RESULT.name_match= str(NAME_MATCH_PERCENTAGE_SERVICE)+' %'
            else:
                NAME_MATCH_PERCENTAGE_SERVICE_1 = getMatchPercent(OCR_TEXT=RC_RESULT.name_of_the_owner.upper(), ADDRESS_STR=name.upper())
                RC_RESULT.name_match= str(NAME_MATCH_PERCENTAGE_SERVICE)+' %' if NAME_MATCH_PERCENTAGE_SERVICE<=NAME_MATCH_PERCENTAGE_SERVICE_1 else str(NAME_MATCH_PERCENTAGE_SERVICE_1)+' %'
       if 'name_of_vehicles_financer' in RC_RESULT.keys() and len(financer_name.strip())>0 and  RC_RESULT.name_of_vehicles_financer.strip() not in [None,"N/A","n/a"] and len(RC_RESULT.name_of_vehicles_financer.strip())>0:
            if financer_name.strip().upper() in RC_RESULT.name_of_vehicles_financer.strip().upper():
                RC_RESULT.financer_match="Yes"
            else:
              RC_RESULT.financer_match="No" 
    if not api_mode:
        application_meta.response_metadata = RC_INSTANCE.metadata

        
        application_meta.response_metadata["input_data"]            = {}
        application_meta.response_metadata["input_data"]["rc_no"]   = application_data.rc

        transaction = []

        transaction.append({
            "api": "RC",
            "billable": billing_details["BILLABLE"],
            "response_code": RC_RESULT.response_code if RC_RESULT.response_code else "500",
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
    
    
    return RC_RESULT, billing_details["BILLABLE"], RC_RESULT.response_code, billing_details["MESSAGE"] if RC_RESULT.response_code != "106" else RC_RESULT.response_message
