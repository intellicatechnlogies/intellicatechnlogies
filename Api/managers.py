from django.db          import models
from datetime           import datetime as dt
from pytz               import timezone
from django.db.models   import F, Count
from openpyxl           import load_workbook
from os                 import getcwd, path as file_path_util


class api_credentials_manager(models.Manager):
    def validate_credentials(self, API_KEY:str=None, APP_ID:str=None):
        user_data = self.filter(
            api_key=API_KEY,
            app_id =APP_ID,
        ).first()

        return True if user_data else False