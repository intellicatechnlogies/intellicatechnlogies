import concurrent.futures
import pandas as pd
from base64      import b64decode, b64encode
from boto3       import client as init_aws_client, resource as init_aws_resource
from botocore    import exceptions as botocore_exceptions
from cv2         import imdecode, imencode, imwrite as write_image_to_disk, line, ellipse, IMREAD_COLOR
from django.conf import settings
from json        import dumps as dump_as_JSON, loads as load_as_JSON
from math        import ceil
from numpy       import ndarray, frombuffer, uint8
from os          import getcwd, path as file_path_util
from random      import getrandbits, sample
from re          import search as regex_search
from string      import ascii_letters, digits
from uuid        import uuid1


def getCompareFaces(image_data, api_mode=False, service_type=""):
    image_titles = list(image_data)
    imagePairs   = [(a, b) for idx, a in enumerate(image_titles) for b in image_titles[idx + 1:]]
    
    dim = len(image_titles)

    with concurrent.futures.ThreadPoolExecutor(max_workers=21) as executor:
        futures = []
        for pair in imagePairs:
            futures.append(
                executor.submit(
                    CompareFaces, 
                        image_data[pair[0]], 
                        image_data[pair[1]], 
                        f"{pair[0]}#{pair[1]}"
                )
            )   
        match_result     = []
        num_img          = len(image_titles)
        num_matches      = 0
        num_mismatches   = 0
        compaired_pairs  = 0
        invalid_matching = 0
        if service_type == "IDR":
            for future in concurrent.futures.as_completed(futures):
                key, match_percentage, matchingFlag, SRC_IMAGE, TRGT_IMAGE = future.result()
                if matchingFlag == "INVALID IMAGE": continue
                if matchingFlag == "INVALID FORMAT GIVEN": continue
                if matchingFlag == "MATCH" or matchingFlag == "SAME_IMAGE":   num_matches += 1 
                if matchingFlag == "NOMATCH": num_mismatches += 1 
                
                TITLE = key.split("#")
                
                TITLE_S = TITLE[0].replace("_INPUT", "")
                TITLE_T = TITLE[1].replace("_INPUT", "")
                
                pair_result_dict = {
                    "SRC_TITLE" : TITLE[0] if api_mode else TITLE_S,
                    "TRGT_TITLE": TITLE[1] if api_mode else TITLE_T,
                    "PERCENT"   : match_percentage,
                    "FLAG"      : matchingFlag,
                }
                
                match_result.append(pair_result_dict)
        else:
            for future in concurrent.futures.as_completed(futures):
                key, match_percentage, matchingFlag, SRC_IMAGE, TRGT_IMAGE = future.result()
                if matchingFlag == "INVALID IMAGE": invalid_matching += 1
                if matchingFlag == "MATCH" or matchingFlag == "SAME_IMAGE":   num_matches += 1 
                if matchingFlag == "NOMATCH": num_mismatches += 1 
                
                TITLE = key.split("#")
                
                TITLE_S = TITLE[0].replace("_INPUT", "")
                TITLE_T = TITLE[1].replace("_INPUT", "")
                
                pair_result_dict = {
                    "SRC_TITLE" : TITLE[0] if api_mode else TITLE_S,
                    "TRGT_TITLE": TITLE[1] if api_mode else TITLE_T,
                    "PERCENT"   : match_percentage,
                    "FLAG"      : matchingFlag,
                }
                
                match_result.append(pair_result_dict)


    if service_type == "IDR":       
        for i in range(1, len(image_titles)+1):
            if i==1:
                continue
            compaired_pairs = compaired_pairs+(i-1)
            if compaired_pairs==num_matches+num_mismatches:
                num_img = i
                break

        OVERVIEW = {
            "NUM_IMG": num_img,
            "MATCH": num_matches,
            "NO_MATCH": num_mismatches
        }
    else:
        OVERVIEW = {
        "NUM_IMG": len(image_titles),
        "MATCH": num_matches,
        "NO_MATCH": num_mismatches,
        "INVALID": invalid_matching
    }
    
    return OVERVIEW, match_result
