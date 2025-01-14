from django.db import models

class event_log(models.Model):
    sno         = models.BigAutoField(primary_key=True)
    datetime    = models.BigIntegerField(null=False, blank=False, default=1901000000)
    description = models.TextField(null=False, blank=True, max_length=200)
    login_id    = models.CharField(null=False, blank=False, max_length=10, default="1901000000")
    log_level   = models.CharField(null=False, blank=False, max_length=12, default="INFORMATION")
    module      = models.CharField(null=False, blank=True, max_length=33)
    resource_id = models.CharField(null=False, blank=True, max_length=40)
    

class transactions_log(models.Model):
    '''
        Transaction logs for executive accounts. It will store the transaction history to generate reports and usage analytics.
    '''
    sno               = models.BigAutoField(primary_key=True)   
    trx_id            = models.CharField(max_length=100, null=False, blank=False, default="ABC123")  
    api_id            = models.CharField(null=False,blank=False,max_length=15,default="RC")                                          # Incrimental counter...
    appl_no           = models.CharField(max_length=75,null=False,blank=False,default="UNDEFINED")  
    product           = models.CharField(null=False, blank=False, max_length=75, default="Personal Loan") # What kind of loan?
    state             = models.CharField(null=False, blank=False, max_length=45, default="Delhi")         # Which state?
    login_id          = models.BigIntegerField(null=False,blank=False,default=1901000000)       # Application number of the application...
    bill_slab         = models.CharField(max_length=2,default="A",null=False,blank=False)                 # Billing slab of the service for a particular set of transactions...
    billable          = models.BooleanField(null=False,blank=False,default=False)                         # Is this trandsaction billable? Are we going to get paid? Whatever...                # Who the user initiated that transaction...
    resp_code         = models.CharField(null=False,blank=False,max_length=5,default="101")               # Response code... (In case of bulk transactions)              # Which API?
    timestamp         = models.BigIntegerField(null=False,blank=False,default=0)                          # date-time stamp of the final record entry...      # Unique Identifier for each set of transactions...
    trx_type          = models.CharField(null=False,blank=False,max_length=12,default="BULK")             # BULK, IDR or just a KYC?
    response_metadata = models.JSONField(null=False,blank=False,default=dict)
    source_resp_time  = models.CharField(max_length=50, null=False, blank=False, default="ABC123")        
    overall_resp_time = models.CharField(max_length=50, null=False, blank=False, default="ABC123")        
