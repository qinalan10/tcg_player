import requests
import pandas as pd 
import json 
from collections import defaultdict
from config import *

# accessing api 
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
    

## MR MIME FUCKS IT UP, ARCEUS FUCKS IT UP, FARFECTCH, mime jr, tapu koko/lele/other one

exclusions = []
# pokemon_names from config file - just a name of all pokemon
for i in pokemon_names:
    exclusions.append(i.lower())
    
name_exclusions = ['m', 'mega', 'shining', 'blaines', 'dark', 'light', 'sabrinas', 'brocks', 'mistys']

# get product ids from a search value
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
    # if there is only one id, it returns a value instead of an array because for some reason the next function doesn't work 
    # with an array of len = 1
    if (len(product_ids)==1):
        product_ids = product_ids[0]
    return product_ids

def get_product_definitions_and_name(product_ids:[int]) -> [dict]:
    global exclusions
    global name_exclusions
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
        string = product['url'].split('/')
        # 6th element in array is setname, name and other info 
        set_names = string[5].split('-')
        ls = []
        for arr in set_names[1:]:
            if ((arr in exclusions or arr in name_exclusions)):
                break
            ls.append(arr)
        set_name = ' '.join(ls)
        clean_name = product['cleanName']
        desc = f'{str(num)}: {clean_name} {set_name} \n'
        #str(num) + ': ' + product['cleanName'] + ' ' + product['url'] + ' \n' 
        names.append(name)
        descs.append(desc)
        product_ids.append(product_id)
        num += 1
        print(desc)
    return names, descs, product_ids
    
    
def get_select_product(product_ids, product_id_element):
    return product_ids[product_id_element]


def get_price(product_id : str) -> None:
    endpoint = "https://api.tcgplayer.com/pricing/product/"
    url = endpoint + product_id
    response = requests.request("GET", url, headers=headers)
    for i in response.json()['results']:
        if (i['marketPrice'] != None):
            print(i['subTypeName'] + ': ' + str(i['marketPrice']))


def breakeven(price = 2, shipping_method = 'stamp', price_threshold = 20):
    # Material Costs (may change if we buy more at bulk)
    penny_sleeve = 0.01768
    top_loader = 0.0765
    team_bag = 0.0607
    
    # shipping costs 
    bubble_mailer = 0.2198
    pirate_ship = 4.5
    stamps = .58
    envelope = .05
    
    # tcg player fee = (subtotal + tax) * 2.3% + 30 cents + subtotal * 10.25% 
    tcg_player_fee = ((price * 1.10) * .023) + .30 + price * .1025
    
    # check for what kind of shipping 
    if (price > price_threshold):
        shipping_method = 'bubble'
    # calculate breakeven costs 
    if shipping_method == 'bubble':
        breakeven_price = price - penny_sleeve - top_loader - team_bag - pirate_ship - bubble_mailer - tcg_player_fee
    else:
        breakeven_price = price - penny_sleeve - top_loader - team_bag - stamps - envelope - tcg_player_fee
    return breakeven_price


def buy_price(breakeven_price, margin = .15):
    even = breakeven(breakeven_price)
    return ((1 - margin) * even)
