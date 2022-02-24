import requests
import pandas as pd 
import json 
from collections import defaultdict
from config import *

# response = requests.post('https://api.tcgplayer.com/token',
                        
#                         headers = {"Content-Type" : "application/json",
#                         "Accept" : "application/json"},
                        
#                         data = (f"grant_type=client_credentials"
#                                 f"&client_id={public_key}&"
#                                 f"client_secret={private_key}"))
response = requests.post(
            "https://api.tcgplayer.com/token",
            
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"},
           
            data=(f"grant_type=client_credentials"
                  f"&client_id={public_key}&"
                  f"client_secret={private_key}")
        )
access = response.json()['access_token']
headers = {"accept": "application/json", 
           "Content-Type": "application/json",
           'User-Agent': 'alan_qin',
           "Authorization": "bearer " + access}
#inventory = pd.read_csv('inventory.csv', headers = True)

    
    
def get_product_ids(search_value:str) -> [int]:
    url = "https://api.tcgplayer.com/catalog/categories/3/search"
    payload = {"sort":"Relevance",
           "filters": [{
              "values": [search_value],
              "name": "productName"
          }],
          "limit":1000}
    response = requests.request('POST', url, json=payload, headers=headers)
    product_ids = response.json()['results']
    if (len(product_ids)==1):
        product_ids = product_ids[0]
    return product_ids

def get_product_definitions_and_name(product_ids:[int]) -> [dict]:
    endpoint = "https://api.tcgplayer.com/catalog/products/"
    productids = str(product_ids)
    url = endpoint + productids
    parameters = {'getExtendedFields':True}
    response = requests.get( url, headers=headers, params = parameters)
    product_definitions = response.json()['results']
    names = []
    descs = []
    product_ids = []
    num = 0
    for product in product_definitions:
        product_id = product['productId']
        name = product['cleanName']
        desc = str(num) + ': ' + product['cleanName'] + ' ' + product['url']
        names.append(name)
        descs.append(desc)
        product_ids.append(product_id)
        num += 1
    return names, descs, product_ids
    
    
def get_select_product(product_ids, product_id_element):
    return product_ids[product_id_element]


def get_price(product_id):
    endpoint = "https://api.tcgplayer.com/pricing/product/"
    url = endpoint + product_id
    response = requests.request("GET", url, headers=headers)
    return response.json()

