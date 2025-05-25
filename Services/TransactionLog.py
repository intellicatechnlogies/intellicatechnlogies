
from Services.models     import transactions_log,service_result
class TransactionLog():
    def createTransactionLog(trx_id:str,api_id:str,login_id:int,billable:str,resp_code:str,timestamp:int,response_data:dict):
        record=transactions_log(trx_id=trx_id,api_id=api_id,appl_no="Test",product="Test",state="Test",login_id=login_id,bill_slab="A",billable=billable,resp_code=resp_code,timestamp=timestamp,trx_type="Test",response_metadata=response_data,source_resp_time="0",overall_resp_time="0")
        record.save()
    def createServiceResult(login_id:int,trx_id:str,timestamp:int,api_id:str,billable:bool):
        record=service_result(login_id=login_id,Application_number='Test',State="Test",request_id=trx_id,service_name=api_id,billable=billable,timestamp=timestamp,result_view=False,result_download=False)
        record.save()