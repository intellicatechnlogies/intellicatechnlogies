from re import compile as compileRegex, match as matchWithRegex

loginID_Regex  = compileRegex("\A['15','18','17','19','13','14','12','11','16']{2}[\d]{1}[1-9]{1}[0]{1}[\d]{5}\Z")

mobile_number_Regex = compileRegex("\A[0-9]{10}\Z")

lpg_cylinder_Regex  =compileRegex("\A[1-9][0-9]{16}\Z")

fssai_Regex         =compileRegex("\A[0-9]{14}\Z")

msme_Regex         =compileRegex("\A^UDYAM[-][A-Z]{2}[-][0-9]{2}[-][0-9]{7}\Z")

ebill_Regex         =compileRegex("\A[A-Za-z0-9]{2,20}\Z")

rc_Regex           =compileRegex("\A[A-Za-z]{2,3}[0-9]{1,2}[A-Za-z]{1,3}[0-9]{1,4}\Z")

service_provider_Regex=compileRegex("\A[A-Za-z0-9_]{2,20}\Z")

dl_number_Regex     = compileRegex(("^(([A-Z]{2}[0-9]{2,3})" + "( )|([A-Z]{2}-[0-9]" + "{2,3}))((00|02|19|20)[0-9]" + "[0-9])[0-9]{6,7}$"))

pan_number_Regex    = compileRegex("\A[A-Za-z]{3}[PCHABGJLFT]{1}[A-Za-z]{1}[0-9]{4}[A-Za-z]{1}\Z")

pan_number_Regex_P    = compileRegex("\A[A-Za-z]{3}[P]{1}[A-Za-z]{1}[0-9]{4}[A-Za-z]{1}\Z")

epic_number_Regex   = compileRegex("\A[A-Za-z]{3}[0-9]{7}\Z")

aadhaar_Regex       = compileRegex("\A[0-9]{12}\Z")

email_id_Regex      = compileRegex("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}")

gst_Regex           = compileRegex('^[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[CZ]{1}[0-9a-zA-Z]{1}$|^[0-9]{4}[a-zA-Z]{3}[0-9]{5}[0-9a-zA-Z]{2}[0-9a-zA-Z]{1}$')

# Validators
RegexValidateLoginID  = lambda loginID : True if matchWithRegex(loginID_Regex, str(loginID)) != None else False
RegexMobile_number    = lambda mobile_number : True if matchWithRegex(mobile_number_Regex, str(mobile_number)) != None else False
RegexFssai_Number          = lambda fssai_number : True if matchWithRegex(fssai_Regex, str(fssai_number)) != None else False
RegexCylinder_number  = lambda lpg_cylinder_number : True if matchWithRegex(lpg_cylinder_Regex, str(lpg_cylinder_number)) != None else False
RegexAadhaar_number    = lambda aadhaar_number : True if matchWithRegex(aadhaar_Regex, str(aadhaar_number)) != None else False
RegexEbill_number     = lambda ebill_Regex_number : True if matchWithRegex(ebill_Regex, str(ebill_Regex_number)) != None else False
RegexMsme_number      =lambda msme_Regex_number : True if matchWithRegex(msme_Regex, str(msme_Regex_number)) != None else False

RegexRC_number       =lambda rc_Regex_number : True if matchWithRegex(rc_Regex, str(rc_Regex_number)) != None else False


RegexService_provider_number= lambda service_provider_Regex_number : True if matchWithRegex(service_provider_Regex, str(service_provider_Regex_number)) != None else False
RegexValidateDL       = lambda dl_number : True if matchWithRegex(dl_number_Regex, str(dl_number)) != None else False
RegexPan_number       = lambda pan_number : True if matchWithRegex(pan_number_Regex, str(pan_number)) != None else False
RegexPan_number_Person      = lambda pan_number : True if matchWithRegex(pan_number_Regex_P, str(pan_number)) != None else False
RegexEpic_number      = lambda epic_number : True if matchWithRegex(epic_number_Regex, str(epic_number)) != None else False
RegexEmail_id         = lambda email_id : True if matchWithRegex(email_id_Regex, str(email_id)) != None else False
Regex_gst             = lambda gst : True if matchWithRegex(gst_Regex, str(gst)) != None else False