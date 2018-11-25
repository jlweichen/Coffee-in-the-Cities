# this parses Starbucks website for location data

from bs4 import BeautifulSoup
import csv

import requests
import time
import googlemaps
import json

import pandas as pd
##################################################
# authentication of Google Maps AI
gmaps = googlemaps.Client(key='xxxxxxxxxxxxxxxxxxxxxxxxx')

##################################################
# functions!

# prompt for city, converts to coords using Google Maps geocoding API
def prompt(zip):
    try:
        geocode_result = gmaps.geocode(zip)
        return geocode_result[0]['geometry']['location']
    except:
        print("Not able to parse zip " + str(zip))
        return
    
# turn the search page's html into soup for parsing
def soupify(zip):
    url = prompt(zip)
    baseurl = "https://www.starbucks.com/store-locator?map="
    geolat = url['lat']
    geolng = url['lng']
    zoom = '8z'
    newurl = baseurl + str(geolat) +','+str(geolng)+','+ zoom
    html = requests.get(newurl)
    time.sleep(3)
    content = html.content
    return BeautifulSoup(content, 'html5lib')

# need coordinates and other data for each store
# this function needs work
# need <div id="bootstrapData"> where the coordinates are held
def storeFind(soup):
    job = soup.find(id='bootstrapData')
    return unicode(job.string)

def zipFrame(zip):
    try:
        soupy = soupify(zip)
        biglist = storeFind(soupy)
        listly = json.loads(biglist)
        stores = listly['storeLocator']['locationState']['locations']
        del(listly, biglist)
        return pd.io.json.json_normalize(stores, errors = 'ignore')
    except:
        return
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
# most important is coords, next important - corp owned or licensed?
# equipment on site? is it a Reserve store? Drive through?
# CO - corporate store, LS - licensed store

zipframe = [zipFrame(i)for i in zips['zip code']]


datadir = '~/data/'

biglist = pd.DataFrame()
for i in range(0, len(zipframe)):
    biglist = biglist.append(zipframe[i])
    
biglist['zip code'] = biglist['address.postalCode']
# removing duplicate locations - there will be a lot!
biglist = biglist.drop_duplicates('id')
biglist.index = range(0, len(biglist))
# truncating zip codes to 5 digits
for i in range(0, len(biglist['address.postalCode'])):
    biglist['zip code'][i] = biglist['address.postalCode'][i][0:5]
    
# more cleaning data - zip code 55111 doesn't have a shapefile
# it is part of the MSP airport
# so we substitute zip code 55450 whose shapefile covers the airport
biglist = biglist.replace(u'55111', u'55450')
biglist.to_csv(datadir+ "twincitysbux.csv", index = False)

# counting the number of stores in each zip code
countcol = (biglist['zip code'].value_counts().reset_index())
countcol.columns = ['zip code', 'count']
zips = pd.merge(zips, countcol, how='left', on=['zip code'])
zips = zips.fillna(0)


zips.to_csv(datadir+ "starbuckscount.csv", index = False)
