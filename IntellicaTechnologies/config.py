"""
    Never hardcode your passwords, or access keys in your program,
    keep them in a seperate file and access...

    Unless you want to dance on 'Billy Jeans' on your keyboard with a panic face.
"""
from decouple import config
from munch import Munch
from termcolor import cprint

cprint(f'\n\n[INFO] Loading Configuration:', color='yellow', attrs=['bold'])
configData = {
    "AWS_CONFIG" : {
        "ACCESS_KEY" : "AKIAYM7POH4LPVJMIN3S",
        "ACCESS_KEY_SECRET" : "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",
        "REGION_NAME" : "us-east-1",
        "AWS_STORAGE_BUCKET_NAME": "intellica-datastore"
    },
    "DATABASE_CONFIG" : {
        "ENGINE" : "django.db.backends.postgresql_psycopg2",
        "NAME" : "Glance_DB",
        "USER" : "TimbleUser",
        "PASSWORD" : "%Xk6xf8b46Rmhmt!2#+HSRk!YgfaX*",
        "HOST" : "glance-db.chtcytbiqc89.ap-south-1.rds.amazonaws.com",
        "PORT" : 5432
    },
    "ZOOP" : {
        "api-key" : "49B7H4X-WS74R6C-GREZH5N-P7Q4F2Q",
        "app-id" : "617c01183a9887001d8e61fa",
    },
    "ZOOP_TEST" : {
        "api-key" : "24B0F1R-X04MVCD-NSW2R84-PM0GQTD",
        "app-id" : "614b0879b69897001ec9af43"
    },
    "KYC_CART" : {
        "x-api-key" : "bbleurwpsd9f5new0w6qkkkupxaa79r1e"
    },   
    "digitap" : {
        "x-api-key" : "Basic NTEzODI4OTY6bU8yZ1VxbGxkYmRsM0l5REdub0s5eU5FNmM1RGFMNG8="
    },      
    "METIS" : {
        "Authorization"   : "Bearer",
        "X-TenantID"      : "https://taasha.tech",
        "Origin"          : "https://app.qanat.in",
        "UsernameIdentity": "faiyaz.ahmad@timbletech.com",
        "password"        : "Test@12345"
    },
    "Sandbox" : {
        "x-api-key" : "key_live_o6Q5TVjfzOzr3LQ38D51DNiogiQ6nbbG",
        "x-api-secret" : "secret_live_sm4hbPu9CYrkvORyZlTuHsQ4HpHYumq7"
    },
    "TruthScreen" : {
        "username" : "prod.timble@authbridge.com"
    },
    "TaxPayer" : {
        "apiKey" : "40da63d2-4fcd-4a28-82bd-c8058cf7aaa1"
    },
    "Signzy" : {
     "Authorization":"fQsBGM592avo4S7SHy0fzpBUAoAY5mqXeI6K1jMSt4x5Yv1W4nr5iwNiDDqQVV89"
    },
    "Zoop_URL" : {
        "base_url" : "https://live.zoop.one/api/v1"
    },
    "ZOOP_TEST_URL" : {
        "base_url" : "https://test.zoop.one/api/v1"
    },
    "KYC_Cart_URL" : {
        "base_url" : "https://api.kyckart.com"
    },
    "METIS_URL" : {
        "base_url" : "https://app.qanat.in:8098"
    },
    "Sandbox_URL" : {
        "base_url" : "https://api.sandbox.co.in"
    },
    "TruthScreen_URL" : {
        "base_url" : "https://www.truthscreen.com"
    },
    "TaxPayer_URL" : {
        "base_url" : "https://taxpayer.irisgst.com/api"
    },
    "Signzy_URL":{
       "base_url" : "https://signzy.tech/api/v2/patrons/650817b911c33b002bafcc15"
    },
    "DIGITAP_URL":{
       "base_url" : "https://svc.digitap.ai"
    },
}

class Config:
    def __init__(self):
        self.config_data  = configData

        # Application config...
        try:    
            GLANCE_ENV = config("GLANCE_ENV")
            if GLANCE_ENV=="PRODUCTION":
                self.DEBUG_MODE = False
                self.PRODUCTION = True
            elif GLANCE_ENV=="STAGING":
                self.DEBUG_MODE = True
                self.PRODUCTION = True
            else:
                self.DEBUG_MODE = True
                self.PRODUCTION = True
        except: 
            GLANCE_ENV      = "LOCAL"
            self.DEBUG_MODE = True
            self.PRODUCTION = False
        
        self.__environment = "settings.production" if GLANCE_ENV == "PRODUCTION" else "settings.staging" if GLANCE_ENV == "STAGING" else "settings.local"

        # Database Config...
        self.__dbConfig    = self.config_data["DATABASE_CONFIG"]
        
        self.__awsConfig   = Munch(self.config_data["AWS_CONFIG"])

        self.__zoop        = Munch(self.config_data["ZOOP"])

        self.__zoop_test   = Munch(self.config_data["ZOOP_TEST"])

        self.__kyc_cart    = Munch(self.config_data["KYC_CART"])
              
        self.__digitap    = Munch(self.config_data["digitap"])
           
        self.__metis    = Munch(self.config_data["METIS"])

        self.__sandbox     = Munch(self.config_data["Sandbox"])

        self.__truthscreen = Munch(self.config_data["TruthScreen"])

        self.__taxpayer    = Munch(self.config_data["TaxPayer"])

        self.__zoop_url    = Munch(self.config_data["Zoop_URL"])

        self.__zoop_test_url = Munch(self.config_data["ZOOP_TEST_URL"])

        self.__kyc_cart_url = Munch(self.config_data["KYC_Cart_URL"])

        self.__metis_url = Munch(self.config_data["METIS_URL"])

        self.__digitap_url = Munch(self.config_data["DIGITAP_URL"])

        self.__sandbox_url  = Munch(self.config_data["Sandbox_URL"])
        self.__truthscreen_url = Munch(self.config_data["TruthScreen_URL"])

        self.__taxpayer_url = Munch(self.config_data["TaxPayer_URL"])
        self.__signzy        = Munch(self.config_data["Signzy"])
        self.__signzy_url = Munch(self.config_data["Signzy_URL"])


    @property
    def isProduction(self):
        return self.PRODUCTION

    @property
    def environment(self):
        '''Server Environment configuration'''
        return self.__environment
    
    @property
    def debug_mode(self):
        return self.DEBUG_MODE

    @property
    def dbConfig(self):
        '''Database configuration'''
        return self.__dbConfig
    
    @property
    def awsConfig(self):
        '''AWS configuration'''
        return self.__awsConfig

    @property
    def zoop(self):
        '''ZOOP credentials'''
        return self.__zoop

    @property
    def zoop_test(self):
        '''ZOOP test credentials'''
        return self.__zoop_test

    @property
    def kyc_cart(self):
        '''KYC_CART credentials'''
        return self.__kyc_cart  
    @property
    def digitap(self):
        '''digitap credentials'''
        return self.__digitap
    
    @property
    def metis(self):
        '''METIS credentials'''
        return self.__metis

    @property
    def sandbox(self):
        '''SANDBOX credentials'''
        return self.__sandbox

    @property
    def truthscreen(self):
        '''Truth Screen credentials'''
        return self.__truthscreen

    @property
    def taxpayer(self):
        '''Tax Payer credentials'''
        return self.__taxpayer

    @property
    def zoop_base_url(self):
        '''Zoop base url'''
        return self.__zoop_url

    @property
    def zoop_test_url(self):
        '''ZOOP test url'''
        return self.__zoop_test_url

    @property
    def kyc_cart_base_url(self):
        '''Kyc Cart url'''
        return self.__kyc_cart_url
    
    @property
    def metis_base_url(self):
        '''Metis url'''
        return self.__metis_url
  
    @property
    def digitap_base_url(self):
        '''Digitap url'''
        return self.__digitap_url
   

    @property
    def sandbox_base_url(self):
        '''Sandbox url'''
        return self.__sandbox_url

    @property
    def truthscreen_url(self):
        '''TruthScreen url'''
        return self.__truthscreen_url

    @property
    def taxpayer_url(self):
        '''TaxPayer url'''
        return self.__taxpayer_url
    @property
    def signzy(self):
        '''Signzy credentials'''
        return self.__signzy
    @property
    def signzy_base_url(self):
        '''Signzy url'''
        return self.__signzy_url

configObj     = Config()
Env           = configObj.environment
getSpaceStr67 = lambda s: ' '*(67-len(str(s)))

cprint(f'  +-------------------------------------------------------------------------------------------------+', color='red', attrs=['bold'])
cprint(f'  |--> [INFO] Environment     : {Env} {getSpaceStr67(Env)}|', color="cyan", attrs=['bold'])
cprint(f'  +-------------------------------------------------------------------------------------------------+', color='red', attrs=['bold'])