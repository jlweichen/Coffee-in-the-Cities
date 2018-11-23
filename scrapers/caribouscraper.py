
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
# need two sections of the page: <div id="collapse-map"> where the coordinates are held
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


with open('~/tczips.csv', 'rb') as f:
    reader = csv.reader(f)
    zips = list(reader)

zips = pd.DataFrame(zips)
zips.columns = ['zip code']
zips.set_index('zip code')
##############################################################
# first a data frame of soup objects for each zip code's results
zipsoup = [soupify(i)for i in zips]
# extracting the store coordinates, street addresses
storeframe = [storeFrame(i)for i in zipsoup]
# extracting the store zip codes
storezips = [zipFrame(i) for i in zipsoup]


datadir = '~/data/'
# creating a dataframe to hold all store info

biglist = pd.DataFrame()
for i in range(len(storeframe)):
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

# removing duplicate locations
biglist = biglist.drop_duplicates('id')
# exporting to file
biglist.to_csv(datadir+ "twincitycaribou.csv", index = False)

# counting the stores per zip code

countcol = (biglist['zip code'].value_counts().reset_index())
countcol.columns = ['zip code', 'count']
zips = pd.merge(zips, countcol, how='left', on=['zip code'])
zips.to_csv(datadir+ "cariboucount.csv", index = False)
