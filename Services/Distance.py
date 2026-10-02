from munch                                  import Munch
from IntellicaTechnologies.GCP              import gmaps_client
class DISTANCE:
    def __init__(self, loc1: str="", loc2: str="",loc3: str="", thresh: int=0):
        self.__result_dict = Munch()
        self.__result_dict.loc_1  = loc1
        self.__result_dict.loc_2  = loc2
        self.__result_dict.loc_3   = loc3 if len(str(loc3))>0 else "N/A"
        self.__result_dict.thresh = thresh
        self.__result_dict.distance=[]
        self.__response_metadata= Munch()


    def getdistpair(self):
        if self.__result_dict.loc_3 !='N/A':
            return (self.__result_dict.loc_1,self.__result_dict.loc_2), (self.__result_dict.loc_2,self.__result_dict.loc_3), (self.__result_dict.loc_3,self.__result_dict.loc_1)
    def getDistanceResult(self):
        OVERVIEW={}
        all_status = []
        distance_result={}
        if self.__result_dict.loc_3 =='N/A':
            distance_result={}
            status       = "CND"
            thresh       = self.__result_dict.thresh
            all_lat_long = gmaps_client.distance_matrix(self.__result_dict.loc_1,self.__result_dict.loc_2)
            dist_res     = all_lat_long["rows"][0]["elements"][0] 
            duration = dist_res["duration"].get("text", None) if "duration" in dist_res.keys() else None
            if dist_res["status"] == "OK":
                destination_addresses=all_lat_long['destination_addresses']
                origin_addresses=all_lat_long['origin_addresses']
                distance     = dist_res["distance"]["text"]
                distance_val = distance.replace("km", "")
                distance_val = distance_val.replace("m", "")
                distance_val = float(distance_val.strip().replace(",",""))
                distance_result["origin_address"]=" ".join(origin_addresses)
                distance_result["destination_address"]="".join(destination_addresses)
                distance_result["distance"]=distance
                distance_result["duration"]=duration
                OVERVIEW["BILLABLE"]="True"
                OVERVIEW["RESP_CODE"]="101"
                OVERVIEW["RESP_MSG"]="This Transaction is part of Billable"
                if thresh>0:
                    if float(distance_val) > float(thresh):
                        status = "MORE"
                    else:
                        status = "WITHIN"
            if dist_res["status"] != "OK":
                OVERVIEW["BILLABLE"]="False"
                OVERVIEW["RESP_CODE"]="500"
                OVERVIEW["RESP_MSG"]="No Distance Found"

            all_status.append(status)
            distance_result["status"]=status
            self.__result_dict.distance.append(distance_result)

        else:
            for location in self.getdistpair():
                distance_result={}
                status       = ""
                thresh       = self.__result_dict.thresh
                all_lat_long = gmaps_client.distance_matrix(location[0],location[1])
                dist_res     = all_lat_long["rows"][0]["elements"][0] 
                duration = dist_res["duration"].get("text", None) if "duration" in dist_res.keys() else None
                if dist_res["status"] == "OK":
                    destination_addresses=all_lat_long['destination_addresses']
                    origin_addresses=all_lat_long['origin_addresses']
                    distance     = dist_res["distance"]["text"]
                    distance_val = distance.replace("km", "")
                    distance_val = distance_val.replace("m", "")
                    distance_val = float(distance_val.strip().replace(",",""))
                    distance_result["origin_address"]=" ".join(origin_addresses)
                    distance_result["destination_address"]="".join(destination_addresses)
                    distance_result["distance"]=distance
                    distance_result["duration"]=duration
                    OVERVIEW["BILLABLE"]="True"
                    OVERVIEW["RESP_CODE"]="101"
                    OVERVIEW["RESP_MSG"]="This Transaction is part of Billable"
                    if thresh>0:
                        if float(distance_val) > float(thresh):
                            status = "MORE"
                        else:
                            status = "WITHIN"
                if dist_res["status"] != "OK":
                    OVERVIEW["BILLABLE"]="False"
                    OVERVIEW["RESP_CODE"]="500"
                    OVERVIEW["RESP_MSG"]="No Distance Found"

                all_status.append(status)
                distance_result["status"]=status
                self.__result_dict.distance.append(distance_result)
        return self.__result_dict,OVERVIEW
    @property
    def result(self):
        results,OVERVIEW = self.getDistanceResult()
        return results,OVERVIEW

       


def getdistance(application_data: Munch=None, application_meta:Munch = None, api_mode=False):
    distance=DISTANCE(application_data['address1'],application_data['address2'],application_data['address3'] if "address3" in application_data.keys() else "",application_data['thresh'] if "thresh" in application_data.keys() else 0)
    DISTANCE_RESULT,OVERVIEW = distance.result
    if not api_mode:
        transaction = []
        application_meta["input_data"]        = {}
        application_meta.input_data["distance"] = application_data
        transaction.append({
                    "api": "DISTANCE",
                    "billable": OVERVIEW["BILLABLE"],
                    "response_code": OVERVIEW["RESP_CODE"],
                })
        # transactions_log.objects.enter_trx_log(
        #     application_number = application_meta.application_number, 
        #     login_id           = application_meta.login_id, 
        #     product            = application_meta.product,
        #     state              = application_meta.state,
        #     transactions       = transaction, 
        #     transactions_type  = application_meta.transactions_type,
        #     response_metadata  = application_meta
        # )
    return DISTANCE_RESULT, OVERVIEW["BILLABLE"], OVERVIEW["RESP_CODE"], OVERVIEW["RESP_MSG"]