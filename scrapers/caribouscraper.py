from bs4 import BeautifulSoup
import csv

import requests
import time

import json
import pandas as pd

import re
##################################################
# functions!

def soupify(zip):
    try:     
        baseurl = "https://locations.cariboucoffee.com/index.html?q="
        newurl = baseurl +str(zip)
        html = requests.get(newurl)
        time.sleep(3)
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

'''
with open('~/Documents/cariboucity/sourcegis/myziplist.csv', 'rb') as f:
    reader = csv.reader(f)
    zips = list(reader)
'''
zips = pd.read_csv('~/Documents/cariboucity/sourcegis/myziplist.csv')
zips['zip code'] = zips['ZCTA5']

##############################################################

# conversion into data frame object
# now to go through the stores and extract the useful info

zipsoup = [soupify(i)for i in zips['zip code']]
# first runthrough gets the point coordinates
storeframe = [storeFrame(i)for i in zipsoup]
# second runthrough gets the zip code and other info
storeaddress = [addressFrame(i) for i in zipsoup]

datadir = '~/Documents/cariboucity/scrapers/data/'


biglist = pd.DataFrame()
for i in range(0,len(storeframe)):
    biglist = biglist.append(storeframe[i])
biglist.index = range(len(biglist))
biglist = biglist.rename(columns = {'altTagText': 'address'})

bigstore = pd.DataFrame()
for i in range(0,len(storeaddress)):
    bigstore = bigstore.append(storeaddress[i])
bigstore.index = range(len(bigstore))

# merging stores and zips 
biglist = biglist.join(bigstore)
# removing duplicate locations - there will be a lot!
biglist = biglist.drop_duplicates('id')

# renumber index column
biglist.index = range(len(biglist))

# parsing feature list
for i in range(0, len(biglist['features'])):
   for j in range(0, len(biglist['features'][i])):
       namely = biglist['features'][i][j]
       print('store ' + str(i))
       if namely in biglist:
           biglist[namely][i] = 1
       else:
           biglist[namely]=0
           biglist[namely][i] = 1

biglist = biglist.drop(['type', 'get_directions_url', 'url', 'features', 'None'], axis=1)
for i in range(0, len(biglist['address'])):
    biglist['address'][i] = biglist['address'][i].replace(u'Location at ', u'')
    
import datetime
biglist.to_csv(datadir+ "twincitycaribou" + str(datetime.date.today()) + ".csv", index = False)

