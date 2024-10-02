from Services.getMatchPercent import getMatchPercent

def nameMatch(name1,name2):
  name1=(name1.upper().replace('MR ','').replace('MR.','').replace('MR. ','').replace('MISS ','').replace('MISS.','').replace('MISS. ','')).strip()
  name2=(name2.upper().replace('MR ','').replace('MR.','').replace('MR. ','').replace('MISS ','').replace('MISS.','').replace('MISS. ','')).strip()
  NAME_MATCH_PERCENTAGE_SERVICE_1=0.0
  NAME_MATCH_PERCENTAGE_SERVICE = getMatchPercent(OCR_TEXT=name1.upper(), ADDRESS_STR=name2.upper())
  if NAME_MATCH_PERCENTAGE_SERVICE == 100.0:
      NAME_MATCH_PERCENTAGE_SERVICE = getMatchPercent(OCR_TEXT=name2.upper(), ADDRESS_STR=name1.upper())
      if NAME_MATCH_PERCENTAGE_SERVICE == 100.0:
        return 'Matched',"True","101","Success"
      else:
       return str(NAME_MATCH_PERCENTAGE_SERVICE)+' %',"True","101","Success"
  else:
      NAME_MATCH_PERCENTAGE_SERVICE_temp = getMatchPercent(OCR_TEXT=name1.replace(' ','').upper(), ADDRESS_STR=name2.replace(' ','').upper())
      if NAME_MATCH_PERCENTAGE_SERVICE_temp == 100.0:
        return 'Matched',"True","101","Success"
      elif NAME_MATCH_PERCENTAGE_SERVICE_temp >=NAME_MATCH_PERCENTAGE_SERVICE:
         return str(NAME_MATCH_PERCENTAGE_SERVICE_temp)+' %',"True","101","Success"
      NAME_MATCH_PERCENTAGE_SERVICE_1 = getMatchPercent(OCR_TEXT=name2.upper(), ADDRESS_STR=name1.upper())
      return str(NAME_MATCH_PERCENTAGE_SERVICE)+' %' if NAME_MATCH_PERCENTAGE_SERVICE<NAME_MATCH_PERCENTAGE_SERVICE_1 else str(NAME_MATCH_PERCENTAGE_SERVICE_1)+' %',"True","101","Success"
  