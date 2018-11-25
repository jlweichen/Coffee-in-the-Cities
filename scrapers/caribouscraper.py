from bs4 import BeautifulSoup
import csv

import requests
import time

import json
import pandas as pd

##################################################
# functions!


# turn the search page's html into soup for parsing
def soupify(zip):
    try:     
        baseurl = "https://locations.cariboucoffee.com/index.html?q="
        newurl = baseurl +str(zip)
        html = requests.get(newurl)
        time.sleep(5)
        content = html.content
        return BeautifulSoup(content, 'html5lib')
    except:
        return

# need coordinates and other data for each store
# this function needs work
# need <div id="collapse-map"> where the coordinates are held
# and "c-address-postal-code" for each store's ZIP
def storeFind(soup):
    job = soup.find(id="collapse-map")
    return job
def zipFind(soup):
    zippy = soup.find_all(class_ = "c-address-postal-code")
    return zippy

def storeFrame(soupy):
    try:
        biglist = storeFind(soupy)
        framey = json.loads(unicode(biglist.text))
        return pd.DataFrame(framey['locs'])
    except:
        return None
def zipFrame(soupy):
    try:
        framey = zipFind(soupy)
        return framey
    except:
        return None
##############################################################    
# importing CSV of Twin Cities zip codes as a list


with open('/Users/jennifer/Documents/starbucks/tczips.csv', 'rb') as f:
    reader = csv.reader(f)
    zips = list(reader)

zips = pd.DataFrame(zips)
zips.columns = ['zip code']

##############################################################


# conversion into data frame object
# now to go through the stores and extract the useful info

zipsoup = [soupify(i)for i in zips['zip code']]
# first runthrough gets the point coordinates, store name, street, town
storeframe = [storeFrame(i)for i in zipsoup]
# second runthrough gets the zip code
storezips = [zipFrame(i) for i in zipsoup]


datadir = '/Users/jennifer/Documents/starbucks/data/'

biglist = pd.DataFrame()
for i in range(0,len(storeframe)):
    biglist = biglist.append(storeframe[i])
biglist.index = range(len(biglist))
# making zip code list
zip_code = []
for i in range(0,len(storezips)):
    for j in range(0, len(storezips[i])):
            zipper = unicode(storezips[i][j].string)
            zip_code.append(zipper)
zip_code = pd.DataFrame(zip_code)
zip_code.columns = ['zip code']

# merging stores and zips 
biglist = biglist.join(zip_code)
# removing duplicate locations - there will be a lot!
biglist = biglist.drop_duplicates('id')
# cleaning data - zip code 55111 doesn't have a shapefile
# it is part of the MSP airport
# so we substitute zip code 55450 whose shapefile covers the airport
biglist = biglist.replace(u'55111', u'55450')
biglist.to_csv(datadir+ "twincitycaribou.csv", index = False)
