from Api.models         import transactions_log
from pytz               import timezone
from datetime           import datetime as dt

class apiTransaction():
    def transactionCreated(apikey:str,trx:str,timestamp:int,service:str):
        record=transactions_log(api_key=apikey,service=service,timestamp=timestamp,trx_id=trx)
        record.save()