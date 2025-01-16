
from Services.models     import transactions_log
class TransactionLog():
    def createTransactionLog(trx_id:str,api_id:str,login_id:int,billable:str,resp_code:str,timestamp:int,response_data:dict):
        record=transactions_log(trx_id=trx_id,api_id=api_id,appl_no="Test",product="Test",state="Test",login_id=login_id,bill_slab="A",billable=billable,resp_code=resp_code,timestamp=timestamp,trx_type="Test",response_metadata=response_data,source_resp_time="0",overall_resp_time="0")
        record.save()