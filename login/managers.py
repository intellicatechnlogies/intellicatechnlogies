from datetime                     import datetime as dt
from django.db                    import models
from munch                        import Munch
from pytz                         import timezone
from random                       import choices as randomChoices
from string                       import ascii_letters, digits
from argon2            import hash_password_raw, low_level as hash_algo
from binascii          import hexlify
from base64            import b64decode, b64encode


# Argon2 Hasher 
get_hash = lambda message, salt: hexlify(hash_password_raw(time_cost=16, memory_cost=1024, parallelism=2, hash_len=64, password=message.encode(), salt=salt.encode(), type=hash_algo.Type.ID)).decode()

class AccountNotExistException(Exception):
    """Exception raised if no account exist for the given login id."""
    def __init__(self):
        super().__init__("Account doesn't exist for the given login id...")

class InsufficientPermissionsException(Exception):
    """Exception raised for insufficient permissions for an action."""
    def __init__(self):
        super().__init__("Insufficient account permissions...")

class AccountDeactivatedException(Exception):
    """Exception raised for deactivated account."""
    def __init__(self):
        super().__init__("Account is deactivated...")

class UserDataManager(models.Manager):
    # Utilities for data processing related to the user account...
    def create_account(self, creator_login_id, boss_id, contact_number, email_address, state, usage_allocation, user_name, office_address):
        """
        Create a new account.
            LOGIN ID:
                From left to right a login ID is a ten digit number structured as follows:
                    First two digits represents the account type:
                        14: Timble Admin
                        15: Timble Customer Support
                        16: Senior Admin
                        17: Reporting Manager
                        18: Executive
                        19: Executive Demo Account
                    
                    Third and fourth digits represent the client ID.
                        00: reserved for product development team, won't be allocated to anyone.
                        01: Timble Technologies Pvt Ltd
                        and so on...
                    
                    Fifth digit represent the account region:
                        0: reserved for product development team, won't be allocated to anyone.
                        1: East India
                        2: West India
                        3: North India
                        4: South India
                        5: Union Territory
                    
                    Last five digits represent the account ID:
                        00000: reserved for product development team, won't be allocated to anyone.
                        00001 to 99999 can be allocated to the users.
            
            PASSWORD:
                Password is a randomly generated ten alpha-numeric string generated during the account creation.
                A password is stored in a hashed form with 128 characters length...
        """
        # Only, Timble Admin, Timble Customer Support, Senior Admin and Reporting manager can create a new account...
        if creator_login_id[:2] in ["14", "15", "16", "17"]:
            # Pull up the account information of the account creator...
            creator_acc_data = self.filter(login_id=creator_login_id).first()
            # If creators account is active...
            if creator_acc_data.login_active:
                creator_permissions = creator_acc_data.permissions
                # If creator have permissions for creating new accounts...
                if creator_permissions["account"]["create_account"]:
                    created_login_id = 0
                    raw_password     = "".join(randomChoices(ascii_letters+digits, k=10))
                    
                    self.create(
                        boss_id        = boss_id,
                        client_id      = "",
                        contact_number = contact_number,
                        created_date   = dt.timestamp(dt.now(tz=timezone("Asia/Kolkata"))),
                        email_address  = email_address,
                        login_id       = created_login_id,
                        office_address = office_address,
                        password       = get_hash(message=raw_password, salt="KDRaFnKRMYuZPnsJkyBJ52uB9MDosi9H5a4LvPGwIbdQI1tj7UurwJ0iingDpjBxJQEMpdcPCauF8VFwKDO46H87f4OMpOl3NUreSbqwwdrguigmoqlJJe0LQNoG3dkb"),
                        permissions    = {},
                        session_info   = {},
                        state          = state,
                        usage_quota    = usage_allocation,
                        user_name      = user_name
                    )
                else:
                    raise InsufficientPermissionsException
            else:
                raise AccountDeactivatedException
    
    def create_demo_execute_account(self, creator_login_id, boss_id, contact_number, email_address, state, usage_allocation, user_name, office_address):
        ...

    def move_demo_account_to_production(self, demo_login_id):
        ...

    def activate_user_account(self, login_id):
        # User account activation...
        user_data = self.filter(login_id=login_id).first()
        if user_data:
            user_data.login_active = True
            user_data.save()
            return True
        return False
    
    def deactivate_user_account(self, login_id):
        # User account deactivation...
        user_data = self.filter(login_id=login_id).first()
        if user_data:
            user_data.login_active = False
            user_data.save()
            return True
        return False
    
    def user_account_details(self, login_id):
        # Get User Account Details...
        ...
    
    def username_to_login_id(self, login_id):
        # Get username from login_id...
        user_data = self.filter(login_id=login_id).first()
        return user_data.user_name if user_data else ""

class UserSessionsManager(UserDataManager):
    def create_session(self, login_id):
        # Create a login session of the user...
        user_data = self.filter(login_id=login_id).first()
        if user_data:
            user_data.last_login = dt.now(timezone("Asia/Kolkata")).strftime(format="%b %d, %Y %I:%M %p")
            user_data.save()
        else:
            raise AccountNotExistException
        
    def update_session(self, login_id):
        # Update the user session...
        ...
    
    def terminate_session(self, login_id):
        # Logout user...
        ...

class activeSessionsManager(models.Manager):
    # Our somewhat reliable attempt to prevent concurrent logins, it prevents concurrent logins.
    def create_login_session(self, request, LOGIN_ID):
        userObj = self.filter(login_id=LOGIN_ID).first()
        if userObj:
            userObj.session_active           = True
            full_session_system_info         = f"OS_{request.user_agent.os.family}_{request.user_agent.os.version_string}__BROWSER_{request.user_agent.browser.family}_{request.user_agent.browser.version_string}__IP_{request.session['IP']}"
            if len(full_session_system_info) > 75:
                full_session_system_info = full_session_system_info[:74]
            userObj.session_system_info      = full_session_system_info
            userObj.session_last_activity_ts = int(dt.timestamp(dt.now(timezone('Asia/Kolkata')))*1000000)
            userObj.save()
            return True
        return False
    
    def terminate_inactive_sessions(self):
        user_records = self.exclude(session_last_activity_ts=0)
        if user_records.count():
            for record in user_records:
                time_difference        =  dt.utcnow() - dt.fromtimestamp(record.session_last_activity_ts/1000000)
                time_difference_in_sec = time_difference.total_seconds()
                if time_difference_in_sec > 3600:
                    print(f"[INFO] Session timeout : Terminating session for : {record.login_id}")
                    record.session_active           = False
                    record.session_system_info      = ""
                    record.session_last_activity_ts = 0
                    record.save()

    def is_session_active(self, LOGIN_ID):
        user_record = self.filter(login_id=LOGIN_ID).first()
        if user_record:
            return user_record.session_active
        return False

    def check_for_active_session(self, LOGIN_ID, request):
        """
        returns:
            (True, "ACTIVE")    : Account is already loged in the same browser in the same browser, OS and IP.
            (False, "ACTIVE")   : Account is already loged in the different compination of browser, OS and IP.
            (True, "TIMEOVER")  : User was inactive for more than one hour and needs to login again.
            (False, "NORECORD") : No active session found for the given combination of login id and password...
        """
        records = self.filter(login_id=LOGIN_ID)
        if records.count() > 0:
            user_session_record    = records.first()
            time_difference        =  dt.utcnow() - dt.fromtimestamp(user_session_record.session_last_activity_ts/1000000)
            time_difference_in_sec = time_difference.total_seconds()
            if time_difference_in_sec > 1800:
                print(f"[INFO] Session timeout detected for : {LOGIN_ID}")
                return (True, "TIMEOVER")
            else:
                # Match user agents and IP...
                if user_session_record.session_system_info==f"OS_{request.user_agent.os.family}_{request.user_agent.os.version_string}__BROWSER_{request.user_agent.browser.family}_{request.user_agent.browser.version_string}":
                    print(f"[INFO] User already loged in from same system : {LOGIN_ID}")
                    return (True, "ACTIVE")
                else:
                    print(f"[INFO] User already loged in from different system : {LOGIN_ID}")
                    return (False, "ACTIVE")
        else:
            print(f"[INFO] No login information found for : {LOGIN_ID}")
            return (False, "NORECORD")
        
    def update_activity_timestamp(self, LOGIN_ID):
        print(f"[INFO] Updating last activity timestamp for : {LOGIN_ID}")
        records = self.filter(login_id=LOGIN_ID)
        if records.count() > 0:
            user_session_record = records[0]
            user_session_record.session_last_activity_ts = int(dt.timestamp(dt.now(timezone('Asia/Kolkata')))*1000000)
            user_session_record.save()
            return True
        else:
            return False
    
    def logout_user(self, LOGIN_ID):
        print(f"[INFO] Terminating session for : {LOGIN_ID}")
        userObj = self.filter(login_id=LOGIN_ID).first()
        userObj.session_active           = False
        userObj.session_system_info      = ""
        userObj.session_last_activity_ts = 0
        userObj.save()
    
    def user_account_details(self, LOGIN_ID):
        user_data = Munch()
        user_obj  = self.filter(login_id=LOGIN_ID).first()
        if user_obj:
            user_data.data_found            = True
            user_data.login_id              = user_obj.login_id
            user_data.enabled_apis          = user_obj.enabled_apis
            user_data.enabled_services      = user_obj.enabled_services
            user_data.email_address         = user_obj.email_address
            user_data.contact_number        = user_obj.contact_number
            user_data.registered_ip_address = user_obj.registered_ip_address
            user_data.login_active          = user_obj.login_active
            user_data.office_address        = user_obj.office_address
            user_data.state                 = user_obj.state
            user_data.application_quota     = user_obj.application_quota
            user_data.user_name             = user_obj.user_name
            user_data.client_name           = user_obj.client_name
            user_data.password              = user_obj.password
            user_data.account_type          = user_obj.user_type
        else:
            user_data.data_found            = False
        
        return user_data

    def username_to_login_id(self, login_id):
        user_data = self.filter(login_id=login_id).first()
        return user_data.user_name if user_data else ""

class loginHistoryManager(models.Manager):
    def record_login_history(self, requestObj):
        self.create(
            login_id = requestObj.session["login_id"],
            user_type = requestObj.session["account_type"],
            login_timestamp = requestObj.session["LAST_ACTIVITY_TIMESTAMP"],
            ip_address = requestObj.session["IP"],
            system_info = f"OS_{requestObj.user_agent.os.family}_{requestObj.user_agent.os.version_string}__BROWSER_{requestObj.user_agent.browser.family}_{requestObj.user_agent.browser.version_string}"
        )