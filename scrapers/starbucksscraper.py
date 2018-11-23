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
gmaps = googlemaps.Client(key='xxxxxxxxxxxxxxxxxxxx')

##################################################
# functions!

# takes a zip code and converts to coords using Google Maps' geocoding API
def prompt(zip):
    try:
        geocode_result = gmaps.geocode(zip)
        return geocode_result[0]['geometry']['location']
    except:
        print("Not able to parse zip " + str(zip))
        return
    
# turns the Starbucks store locator results html into 'soup' for parsing
def soupify(zip):
    url = prompt(zip)
    baseurl = "https://www.starbucks.com/store-locator?map="
    geolat = url['lat']
    geolng = url['lng']
    zoom = '8z' # this can be zoomed in with a larger number like 14z or out with a smaller one like 6z
    newurl = baseurl + str(geolat) +','+str(geolng)+','+ zoom
    html = requests.get(newurl)
    time.sleep(3) # three second pause between queries
    content = html.content
    return BeautifulSoup(content, 'html5lib')

# need coordinates and other data for each store
# this function extracts the section of the HTML with the relevant info as a Unicode string
def storeFind(soup):
    job = soup.find(id='bootstrapData')
    return unicode(job.string)

# this function converts the unicode, which is JSON, into a Pandas dataframe
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
# importing CSV of Twin Cities metro zip codes as a list, then convert to single column dataframe
# data from the shapefile "Census 2000 5-Digit ZIP Code Tabulation Areas (ZCTAs)"
# see https://gisdata.mn.gov/dataset/us-mn-state-metc-society-census2000tiger-zcta

with open('~/tczips.csv', 'rb') as f:
    reader = csv.reader(f)
    zips = list(reader)
    
zips = pd.DataFrame(zips)
zips.columns = ['zip code']
zips.set_index('zip code')
##############################################################


# now to go through the stores and extract the info

zipframe = [zipFrame(i)for i in zips]


# preparing to combine all store data into one table
datadir = '~/data/'

biglist = pd.DataFrame()
for i in zipframe:
    biglist = biglist.append(i)
# removing duplicate locations
biglist = biglist.drop_duplicates('id')
# ensuring the table index is correct
biglist.index = range(0, len(biglist))
# truncating zip+4 codes into five digit codes
for i in range(0, len(biglist['address.postalCode'])):
    biglist['zip code'][i] = biglist['address.postalCode'][i][0:5]
# exporting this table to file
biglist.to_csv(datadir+ "twincitysbux.csv", index = False)

# counting the number of stores in each zip code
countcol = (biglist['zip code'].value_counts().reset_index())
countcol.columns = ['zip code', 'count']
zips = pd.merge(zips, countcol, how='left', on=['zip code'])
zips = zips.fillna(0)
# exporting the count of stores per TC area zip code to file
zips.to_csv(datadir+ "starbuckscount.csv", index = False)
