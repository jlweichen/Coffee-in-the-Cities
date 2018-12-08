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


with open('~/tczips.csv', 'rb') as f:
    reader = csv.reader(f)
    zips = list(reader)

zips = pd.DataFrame(zips)
zips.columns = ['zip code']

##############################################################

# conversion into data frame object
# now to go through the stores and extract the useful info

zipsoup = [soupify(i)for i in zips['zip code']]
# first runthrough gets the point coordinates
storeframe = [storeFrame(i)for i in zipsoup]
# second runthrough gets the zip code and other info
storeaddress = [addressFrame(i) for i in zipsoup]

datadir = '~/data/'

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
# cleaning data - zip code 55111 doesn't have a shapefile
# it is part of the MSP airport
# so we substitute zip code 55450 whose shapefile covers the airport
biglist = biglist.replace(u'55111', u'55450')

# making sure only stores with a TC area zip are in the frame
biglist = biglist.merge(zips, on='zip code', how='inner')

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
biglist.to_csv(datadir+ "twincitycaribou.csv", index = False)

# creating list of store counts by zip code
countcol = (biglist['zip code'].value_counts().reset_index())
countcol.columns = ['zip code', 'count']
zips = pd.merge(zips, countcol, how='left', on=['zip code'])
zips = zips.fillna(0)
# exporting it to CSV
zips.to_csv(datadir+ "cariboucount.csv", index = False)
