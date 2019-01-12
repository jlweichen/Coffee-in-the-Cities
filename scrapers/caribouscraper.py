
from bs4 import BeautifulSoup

import requests
import time

import json
import pandas as pd

import re
import datetime

datadir = '~/cariboucity/scrapers/data/'
##################################################
# functions!

def soupify(zip):
    try:     
        baseurl = "https://locations.cariboucoffee.com/index.html?q="
        newurl = baseurl +str(zip)
        html = requests.get(newurl)
        time.sleep(0.2)
        content = html.content
        return BeautifulSoup(content, 'html5lib')
    except:
        return

# need coordinates and other data for each store
# need <div id="collapse-map"> where the coordinates are held

def storeFrame(soupy):
    try:
        biglist = soupy.find(id="collapse-map")
        framey = json.loads(unicode(biglist.text))
        return pd.DataFrame(framey['locs'])
    except:
        return None
# the rest of what we want is elsewhere on the page
# "c-address-postal-code" for town name
# and "c-address-postal-code" for each store's ZIP
# finally <div class="Teaser-amenities"> for each store's features
# each store is a list item
# for example:
#<li class="ResultList-item ResultList-item--ordered js-location-result" id="js-yl-8865338">

def addressFrame(soupy):
    try:
        listing = soupy.find_all(class_ ="Teaser Teaser--locator")
        store = []

        for i in range(0, len(listing)):
            zippy = listing[i].find(class_ = "c-address-postal-code")
            town = listing[i].find(class_ = "c-address-city")
            name = listing[i].find(class_ = "Teaser-titleLink Link Link--standard Text--bold")
            name = (name.text).replace('Caribou Coffee ', '')
            
            if listing[i].find(class_ = "Teaser-amenities") is not None:
                features = listing[i].find(class_ = "Teaser-amenities")
                featList = str(features.text)
                featList = featList.replace('Amenities: ', '')
                featList = featList.replace('Wi-Fi' , 'WiFi')
                featList = re.split(', ', featList)
                
                store.append({'city': town.text, 'zip code': zippy.text, 'features': featList, 'name': name})
            else:
                featList = ['None']
                store.append({'city': town.text, 'zip code': zippy.text, 'features': featList, 'name': name})
            
            storey = pd.DataFrame(data = store)

        return storey

    except:
        return None

##############################################################    
# importing CSV of Twin Cities zip codes as a list

def zipper(path):
    zips = pd.read_csv(path, header = 0,  names = {'zip code'})
    return zips['zip code'].tolist()

##############################################################

# conversion into data frame object
# now to go through the stores and extract the useful info

def bigframe():
    zipsoup = map(soupify, zipper('/Users/jennifer/Documents/cariboucity/sourcegis/myziplist.csv'))
    # first runthrough gets the point coordinates
    storeframe1 = map(storeFrame, zipsoup)
    # second runthrough gets the zip code and other info
    storeframe2 = map(addressFrame, zipsoup)

    bigpoint = pd.concat(storeframe1).rename(columns = {'altTagText': 'address'})
    bigpoint.index = range(len(bigpoint))
    bigaddr = pd.concat(storeframe2)
    bigaddr.index = range(len(bigaddr))

    # merging stores and zips 
    bigpoint = bigpoint.join(bigaddr)
    # removing duplicate locations - there will be a lot!
    bigpoint = bigpoint.drop_duplicates('id')
    bigpoint['brand'] = 'Caribou'
    # renumber index column
    bigpoint.index = range(len(bigpoint))
    return bigpoint

# parsing feature list
def featurizer(table, col):
    column = table[col]
    
    def namer(featurename, i):
        if featurename in table:
            table[featurename][i] = 1
        else:
            table[featurename]=0
            table[featurename][i] = 1
        return

    for i in range(0, len(column)):
        for j in range(0, len(column[i])):
            feat = column[i][j]
            namer(feat, i)
            print('store ' + str(i))      
    return

# the function that pulls it all together and returns a dataframe
def bouFrame():
    big = bigframe()
    featurizer(big, 'features')
    big = big.drop(['type', 'get_directions_url', 'url', 'features', 'None'], axis=1)
    big['address'] = big['address'].apply(lambda x: x.replace(u'Location at ', u''))
    big['brand'] = 'Caribou'

    # cleaning city name data

    goodcities = {'St.Paul': 'St. Paul', 'ROBBINSDALE': 'Robbinsdale',
             'Saint Louis Park': 'St. Louis Park', 'St Louis Park': 'St. Louis Park', 
             'Saint Paul': 'St. Paul', 'St Paul': 'St. Paul',
             'COTTAGE GROVE': 'Cottage Grove', 'SHAKOPEE': 'Shakopee', 'MINNEAPOLIS': 'Minneapolis',
             'SAVAGE': 'Savage', 'NORTHFIELD': 'Northfield'}
    goodindex = goodcities.keys()

    for i in range(len(goodindex)):
        big['city'] = big['city'].replace(goodindex[i], goodcities[goodindex[i]])
        
    big.to_csv(datadir+ "twincitycaribou2" + str(datetime.date.today()) + ".csv", index = False)
    return big
