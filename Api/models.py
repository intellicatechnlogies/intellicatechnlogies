from django.db import models
from Api.managers import api_credentials_manager

class apiUser(models.Model):
    sno              = models.AutoField(primary_key=True)
    api_key          = models.CharField(null=False, blank=False, max_length=36, default="ABCDWXYZ")
    app_id           = models.CharField(null=False, blank=False, max_length=36, default="ABCDWXYZ")
    client           = models.CharField(null=False, blank=False, max_length=50, default="Intellica Technologies Pvt Ltd")
    platform         = models.CharField(null=False, blank=False, max_length=36, default="ABCDWXYZ")
    usage_quota      = models.IntegerField(null=False, blank=False, default=500)
    assigned_api     = models.JSONField(null=False, blank=False, default=dict)
    is_active        = models.BooleanField(null=False, blank=False, default=True)
    objects          = api_credentials_manager()

class transactions_log(models.Model):
    sno              = models.AutoField(primary_key=True)
    api_key          = models.CharField(null=False, blank=False, max_length=36, default="ABCDWXYZ")
    service          = models.CharField(null=False, blank=False, max_length=100, default="ABCDWXYZ")
    timestamp        = models.BigIntegerField(null=False,blank=False,default=0)                          # date-time stamp of the final record entry...
    trx_id           = models.CharField(max_length=40, null=False, blank=False, default="ABC123")
