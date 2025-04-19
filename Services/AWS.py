import concurrent.futures
import pandas as pd
from base64      import b64decode, b64encode
from boto3       import client as init_aws_client, resource as init_aws_resource
from botocore    import exceptions as botocore_exceptions
#from cv2         import imdecode, imencode, imwrite as write_image_to_disk, line, ellipse, IMREAD_COLOR
from django.conf import settings
from json        import dumps as dump_as_JSON, loads as load_as_JSON
from math        import ceil
from numpy       import ndarray, frombuffer, uint8
from os          import getcwd, path as file_path_util
from random      import getrandbits, sample
from re          import search as regex_search
from string      import ascii_letters, digits
from uuid        import uuid1
from Services.TransactionLog  import TransactionLog
from datetime                               import datetime as dt
from pytz                                   import timezone
from IntellicaTechnologies.config import Config

configObj  = Config()
AWS_CONFIG = configObj.awsConfig

s3_resource        = lambda: init_aws_resource('s3',          aws_access_key_id=AWS_CONFIG.ACCESS_KEY, aws_secret_access_key=AWS_CONFIG.ACCESS_KEY_SECRET, region_name=AWS_CONFIG.REGION_NAME)
#dynamodb           = lambda: init_aws_resource('dynamodb',    aws_access_key_id=AWS_CONFIG.ACCESS_KEY, aws_secret_access_key=AWS_CONFIG.ACCESS_KEY_SECRET, region_name=AWS_CONFIG.REGION_NAME)
rekognition_client = init_aws_client('rekognition',           aws_access_key_id=AWS_CONFIG.ACCESS_KEY, aws_secret_access_key=AWS_CONFIG.ACCESS_KEY_SECRET, region_name=AWS_CONFIG.REGION_NAME)
#textract           = lambda: init_aws_client(  'textract',    aws_access_key_id=AWS_CONFIG.ACCESS_KEY, aws_secret_access_key=AWS_CONFIG.ACCESS_KEY_SECRET, region_name=AWS_CONFIG.REGION_NAME)

gen_file_name = lambda: "".join(sample(ascii_letters+digits+ascii_letters, k=48))+".png"

collection_name = "IntellicaTest"

# def base64_to_np_arr(base64_str):
#     im_bytes = b64decode(base64_str)
#     im_arr = frombuffer(im_bytes, dtype=uint8)
#     return imdecode(im_arr, flags=IMREAD_COLOR)

# def np_arr_to_bytes(np_arr, extn=".jpeg"):
#     _, im_arr = imencode(extn, np_arr)
#     return b64encode(im_arr.tobytes())


"""
     ██████╗  ██████╗  ███╗   ███╗ ██████╗   █████╗  ██████╗  ███████╗
    ██╔════╝ ██╔═══██╗ ████╗ ████║ ██╔══██╗ ██╔══██╗ ██╔══██╗ ██╔════╝
    ██║      ██║   ██║ ██╔████╔██║ ██████╔╝ ███████║ ██████╔╝ █████╗  
    ██║      ██║   ██║ ██║╚██╔╝██║ ██╔═══╝  ██╔══██║ ██╔══██╗ ██╔══╝  
    ╚██████╗ ╚██████╔╝ ██║ ╚═╝ ██║ ██║      ██║  ██║ ██║  ██║ ███████╗
     ╚═════╝  ╚═════╝  ╚═╝     ╚═╝ ╚═╝      ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚══════╝
                                                                
                    ███████╗  █████╗   ██████╗ ███████╗ ███████╗    
                    ██╔════╝ ██╔══██╗ ██╔════╝ ██╔════╝ ██╔════╝    
                    █████╗   ███████║ ██║      █████╗   ███████╗    
                    ██╔══╝   ██╔══██║ ██║      ██╔══╝   ╚════██║    
                    ██║      ██║  ██║ ╚██████╗ ███████╗ ███████║    
                    ╚═╝      ╚═╝  ╚═╝  ╚═════╝ ╚══════╝ ╚══════╝    
"""

# def base64_to_np_arr(base64_str):
#     im_bytes = b64decode(base64_str)
#     im_arr = frombuffer(im_bytes, dtype=uint8)
#     return imdecode(im_arr, flags=IMREAD_COLOR)

def CompareFaces(sourceimgstring: str, targetimgstring: str, key=None, sim=0):
    if sourceimgstring == targetimgstring and (sourceimgstring != "" and targetimgstring != ""):
        matchSimilarity = 100.000
        return (key, matchSimilarity, "SAME_IMAGE", sourceimgstring, targetimgstring)
    else:
        matchSimilarity = 0
        try:
            response = rekognition_client.compare_faces(
                SimilarityThreshold = sim,
                SourceImage = {'Bytes': b64decode(sourceimgstring)},
                TargetImage = {'Bytes': b64decode(targetimgstring)}
            )
            
            faceMatch       = response['FaceMatches']
            matchSimilarity = round(float(faceMatch[0]['Similarity']), 3)

            if matchSimilarity >= 60:
                return (key, matchSimilarity, "MATCH", sourceimgstring, targetimgstring)
            else:
                return (key, matchSimilarity, "NOMATCH", sourceimgstring, targetimgstring)
        except rekognition_client.exceptions.InvalidParameterException:
            return (key, matchSimilarity, "INVALID IMAGE", sourceimgstring, targetimgstring)
        except rekognition_client.exceptions.ImageTooLargeException:
            return (key, matchSimilarity, "IMAGE TOO LARGE", sourceimgstring, targetimgstring)
        except rekognition_client.exceptions.InvalidImageFormatException:
            return (key, matchSimilarity, "INVALID FORMAT GIVEN", sourceimgstring, targetimgstring)
        except Exception as e:
            if "Invalid base64-encoded string" in str(e):
                return (key, matchSimilarity, "Invalid base64-encoded string", sourceimgstring, targetimgstring)

            return (key, matchSimilarity, "SERVICE_DOWN", sourceimgstring, targetimgstring)

def getCompareFaces(image_data,service,transaction,api_mode:False,service_type):
    userId=1111
    if "userId" in image_data.keys():
        userId=image_data['userId']
        del image_data['userId']
    image_titles = list(image_data)

    imagePairs   = [(a, b) for idx, a in enumerate(image_titles) for b in image_titles[idx + 1:]]
    
    dim = len(image_titles)
   
    with concurrent.futures.ThreadPoolExecutor(max_workers=21) as executor:
        futures = []
        response_data={}
        for pair in imagePairs:
            timestamp=int(dt.timestamp(
                dt.now(timezone("Asia/Kolkata")))*1000000)
            TransactionLog.createTransactionLog(transaction,service,userId,True,"101",timestamp,response_data)
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

def b64Hit(base64_string):
    try:
        regex_search('(^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$)', base64_string).group(1)
        return True
    except:
        return False

def IMG2PNG(image_base64):
    """
        Allows for the download an s3 object as base64 string.
        of file in S3
            :param s3_file_name: File name
            :return: Tuple of boolian flag and base64 string or error code
    """
    try:
        if b64Hit(base64_string=image_base64):
            S3                      = s3_resource()
            s3_file_name            = f"IMG/{uuid1(getrandbits(48))}.png"
            S3.Object(AWS_CONFIG.AWS_STORAGE_BUCKET_NAME, s3_file_name).put(Body=image_base64)
            converted_base64_string = S3.Object(AWS_CONFIG.AWS_STORAGE_BUCKET_NAME, s3_file_name).get()['Body'].read().decode("utf-8")
            S3.Object(AWS_CONFIG.AWS_STORAGE_BUCKET_NAME, s3_file_name).delete()

            return converted_base64_string
        else:
            return False
    except Exception as ex:
        print(ex)
        return False

def upload_Image_to_s3(image_base64):
    s3_image_id  = str(uuid1(getrandbits(48)))
    #s3_file_name = f"intellica-datastore/{s3_image_id}.png"
    s3_file_name = f"intellica-datastore/{s3_image_id}.json"
    if b64Hit(base64_string=image_base64):
        dict1={}
        dict1['img']=image_base64
        # S3 = s3_resource()
        # S3.Object("intellica-datastore", s3_file_name).put(Body=image_base64)
        s3_resource().Object("intellica-datastore", f"{s3_file_name}").put(Body=dump_as_JSON(dict1))
    
    return s3_file_name

def upload_JSON_to_s3(input_dict,s3_file_name=None):
    """
        Allows for the upload of a dict to a s3 object, may need fleshing out down the line, returns location
        of file in S3
            :param s3_bucket_name: S3 bucket name to push dict/JSON to
            :param s3_file_name: File name
            :param input_dict: input dictionary to push to S3 as JSON
            :return: Tuple of bucket_name and s3_file_name
    """
    s3_file_name = f"intellica-datastore/{s3_file_name}.json"
    
    s3_resource().Object("intellica-datastore", f"{s3_file_name}").put(Body=dump_as_JSON(input_dict))
    
    return s3_file_name.replace(".json","")

def upload_Pdf_to_s3(response,s3_file_name=None):
    """
        Allows for the upload of a dict to a s3 object, may need fleshing out down the line, returns location
        of file in S3
            :param s3_bucket_name: S3 bucket name to push dict/JSON to
            :param s3_file_name: File name
            :param input_dict: input dictionary to push to S3 as JSON
            :return: Tuple of bucket_name and s3_file_name
    """
    s3_file_name = "{s3_file_name}.pdf"
    
    #s3_resource().Object("s3-pdf-store", f"{s3_file_name}").put(Body=dump_as_JSON(input_dict))
    s3_resource.upload_file(response,"s3-pdf-store",s3_file_name)
    
    return s3_file_name

def download_pdf_from_s3(s3_file_name, service="IDR"):
    """
        Allows for the download an s3 object as base64 string.
        of file in S3
            :param s3_file_name: File name
            :return: Tuple of boolian flag and base64 string or error code
    """
    try:
        if service == "IDR"      : bucket = settings.AWS_STORAGE_BUCKET_NAME
        elif service == "FSEARCH": bucket = settings.AWS_FS_REPO_BUCKET_NAME
        
        pdf_base64_string = b64encode(s3_resource().Object(bucket, s3_file_name).get()['Body'].read()).decode("utf-8")
        return (True, pdf_base64_string)
    except botocore_exceptions.ClientError as ex:
        if ex.response['Error']['Code'] == "404":
            # The object does not exist.
            return (False, 404)
        else:
            # Something went wrong!
            return (False, 500)

def download_json_from_S3(s3_file_name):
    """
        Allows for the download a JSON from s3 as a dict.
        of file in S3
            :param s3_file_name: File name
            :return: Tuple of boolian flag and dict or error code
    """
    try: 
        # if service in ["ERPV", "IDR"]: bucket = settings.AWS_STORAGE_BUCKET_NAME
        # elif service == "FSEARCH"    : bucket = settings.AWS_FS_REPO_BUCKET_NAME
        JSON_from_s3 = load_as_JSON(s3_resource().Object("intellica-datastore", s3_file_name).get()["Body"].read().decode('utf-8'))
        return (True, JSON_from_s3)
    except botocore_exceptions.ClientError as ex:
        if ex.response['Error']['Code'] == "404":
            # The object does not exist.
            return (False, 404)
        else:
            # Something went wrong!
            return (False, 500)
        

def getFaceAnalysis(sourceimgstring: str):
    # if sourceimgstring == targetimgstring and (sourceimgstring != "" and targetimgstring != ""):
    #     matchSimilarity = 100.000
    #     return (key, matchSimilarity, "SAME_IMAGE", sourceimgstring, targetimgstring)
    # else:
    #     matchSimilarity = 0
        # try:
            response = rekognition_client.detect_faces(
                #Attributes= [ "ALL" ],
                Attributes= [ "GENDER","AGE_RANGE","FACE_OCCLUDED","EYES_OPEN"],
                Image = {'Bytes': b64decode(sourceimgstring)}
            )
            faceMatch       = response['FaceDetails'][0]
            # matchSimilarity = round(float(faceMatch[0]['Similarity']), 3)

            # if matchSimilarity >= 60:
            #     return (key, matchSimilarity, "MATCH", sourceimgstring, targetimgstring)
            # else:
            #     return (key, matchSimilarity, "NOMATCH", sourceimgstring, targetimgstring)
            return (faceMatch)
        # except rekognition_client.exceptions.InvalidParameterException:
        #     return (key, matchSimilarity, "INVALID IMAGE", sourceimgstring, targetimgstring)
        # except rekognition_client.exceptions.ImageTooLargeException:
        #     return (key, matchSimilarity, "IMAGE TOO LARGE", sourceimgstring, targetimgstring)
        # except rekognition_client.exceptions.InvalidImageFormatException:
        #     return (key, matchSimilarity, "INVALID FORMAT GIVEN", sourceimgstring, targetimgstring)
        # except Exception as e:
        #     if "Invalid base64-encoded string" in str(e):
        #         return (key, matchSimilarity, "Invalid base64-encoded string", sourceimgstring, targetimgstring)

        #     return (key, matchSimilarity, "SERVICE_DOWN", sourceimgstring, targetimgstring)



# def extract_tables(image_arr, column_names):
#     def np_arr_to_bytes(np_arr:ndarray):
#         """
#             Converts a numpy arrey to bytes...
#         """
#         _, im_arr = imencode('.png', np_arr)
#         return im_arr.tobytes()

#     def map_blocks(blocks, block_type):
#         return{
#             block['Id'] : block
#             for block in blocks
#             if block['BlockType'] == block_type
#         }

#     def get_children_ids(block):
#         for rels in block.get('Relationships', []):
#             if rels['Type'] == "CHILD":
#                 yield from rels['Ids']
    
#     def crop_tables(pt1, pt2, img_arr):
#         Xi, Yi = pt1
#         Xf, Yf = pt2
#         return img_arr[Yi:Yf, Xi:Xf].copy()
    
#     H, W, _, = image_arr.shape

#     response = textract().analyze_document(
#         Document={
#             'Bytes': np_arr_to_bytes(image_arr)
#         },
#         FeatureTypes = ['TABLES']
#     )

#     blocks = response['Blocks']
#     tables = map_blocks(blocks, 'TABLE')
#     cells  = map_blocks(blocks, 'CELL')
#     blocks = response['Blocks']
#     words  = map_blocks(blocks, 'WORD')
#     selections = map_blocks(blocks, 'SELECTION_ELEMENT')

#     table_data = []
#     for table_id, table in tables.items():
#         print(table_id)
#         #Determine all the cells that belong to this table
#         table_cells = [cells[cell_id] for cell_id in get_children_ids(table)]
#         n_rows = max(cell['RowIndex'] for cell in table_cells)
#         n_cols = max(cell['ColumnIndex'] for cell in table_cells)
#         content = [[None for _ in range(n_cols)] for _ in range(n_rows)]

#         # Fill in each cell
#         for cell in table_cells:
#             cell_contents = [
#                 words[child_id]['Text']
#                 if child_id in words
#                 else selections[child_id]['SelectionStatus']
#                 for child_id in get_children_ids(cell)
#             ]
#             i = cell['RowIndex'] - 1
#             j = cell['ColumnIndex'] - 1
#             content[i][j] = ' '.join(cell_contents)

        
#         # We assume that the first row corresponds to the column names
#         dataframe = pd.DataFrame(content)
#         if len(dataframe.columns) == len(column_names):
#             dataframe = pd.DataFrame(content,columns=column_names)
#             #Bank statement should have atleast 4 columns...
#             if n_cols == len(column_names):
#                 table_coords = tables[table_id]['Geometry']['Polygon']
#                 c0, _, c2, _ = table_coords
#                 cropped_table_region = crop_tables(pt1=(ceil(c0["X"]*W), ceil(c0["Y"]*H)), pt2=(ceil(c2["X"]*W), ceil(c2["Y"]*H)), img_arr=image_arr)

#                 table_data.append((dataframe, cropped_table_region))
            
#     return table_data