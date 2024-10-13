import googlemaps
import os
from google.cloud import vision
from requests import request as make_HTTP_request
import requests     

gmaps_client = googlemaps.Client(key = "AIzaSyBQgTTMIMbkSSmUxs-JWjX0IJuC8PKvSiw")
#gmaps_client = googlemaps.Client(key = "AIzaSyA21_zzjprmXaDqK9MkiNQRHZxgYnNnpaE")

def reverse_geocoding(LAT, LONG) -> str:
    if LAT and LONG:
        resp = make_HTTP_request(
            method="GET", 
            url=f"https://maps.googleapis.com/maps/api/geocode/json?latlng={LAT},{LONG}&key=AIzaSyBQgTTMIMbkSSmUxs-JWjX0IJuC8PKvSiw"
        )

        response_data = resp.json()
        formatted_address = response_data['results'][0]['formatted_address']
        return formatted_address
    else:
        return ""
    
def get_coordinates(address):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={gmaps_client}'
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None

def find_nearest_bank_branch( user_address):
    user_coords = get_coordinates(user_address)
    
    if user_coords:
        bank_search_url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={user_coords[0]},{user_coords[1]}&radius=5000&type=bank&key={gmaps_client}'
        bank_response = requests.get(bank_search_url)
        bank_data = bank_response.json()
        
        if bank_data['status'] == 'OK' and len(bank_data['results']) > 0:
            nearest_bank = bank_data['results'][0]
            return nearest_bank['name'], nearest_bank['vicinity']
    
    return None

# google_api_key = "AIzaSyA21_zzjprmXaDqK9MkiNQRHZxgYnNnpaE"
# user_address = "B-5/68, Safdarjung Enclave, Humayunpur, Safdarjung Enclave, New Delhi, Delhi 110029"
# # user_address = "VILLAGE BHAGWANPUR POST OFFICE FATEHPUR TEKARI POLICE STATION TEKARI 824236 GAYA"

# nearest_bank_info = find_nearest_bank_branch(google_api_key, user_address)
# if nearest_bank_info:
#     print(f"Nearest Bank: {nearest_bank_info[0]}\nAddress: {nearest_bank_info[1]}")
# else:
#     print("No nearby bank branches found.")


class DISTANCE:
    def __init__(self, loc1: str="", loc2: str="", thresh: int=0):
        self.__loc_1  = loc1
        self.__loc_2  = loc2
        self.__thresh = thresh

    def getDistanceResult(self):
        distance_val, final_distance_text = "", ""
        status       = "CND"
        thresh       = float(self.__thresh)
        all_lat_long = gmaps_client.distance_matrix(self.__loc_1, self.__loc_2)
        dist_res     = all_lat_long["rows"][0]["elements"][0]
        if dist_res["status"] == "OK":
            distance     = dist_res["distance"]
            distance_val = distance["text"]
            final_distance_text = distance_val
            distance_val = distance_val.replace("km", "")
            distance_val = distance_val.replace("m", "")
            distance_val = float(distance_val.strip().replace(",",""))

        if float(distance_val) > float(thresh):
            status = "MORE"
        else:
            status = "WITHIN"
        return final_distance_text, status

def get_raw_text_tokens(image_base64: str=""):
    image   = vision.Image(content=image_base64.decode() if type(image_base64) == bytes else image_base64)
    ocr_res = vision.ImageAnnotatorClient.from_service_account_json(os.path.join(os.getcwd(), "GCV_KEY.json")).document_text_detection(image=image)
    if ocr_res.error.message:
        print("ERROR IN OCR!")
        return ["ERROR"]
    
    text_tokens = []
    for page in ocr_res.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                text = ""
                for word in paragraph.words:
                    for symbol in word.symbols:
                        text += symbol.text
                text_tokens.append(text.upper())
    
    return text_tokens

def ocr(content, api_mode=False):
    image    = vision.Image(content=content.decode() if type(content) == bytes else content)
    response = vision.ImageAnnotatorClient.from_service_account_json(os.path.join(os.getcwd(), "GCV_KEY.json")).document_text_detection(image=image)
    texts    = response.text_annotations
    if response.error.message:
        print(response.error.message)
        response = "error"
    else:
        try:
            t_text = str(texts[0].description)
            if not api_mode:
                t_list = t_text.replace('\n', ' ').split()
                response = ' '.join(t_list)
            else:
                response = t_text
        except:
            response = "NA"
    return response

bytes_to_text_tokens = lambda img_data: [token.upper() for token in ocr(img_data).split("\n")]
bytes_to_text        = lambda img_data: " ".join(bytes_to_text_tokens(img_data=img_data))