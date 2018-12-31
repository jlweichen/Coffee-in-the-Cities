# this parses Starbucks website for location data

from bs4 import BeautifulSoup


import requests
import time
import googlemaps
import json

import pandas as pd
##################################################
# auhtentication of Google Maps AI
gmaps = googlemaps.Client(key='AIzaSyAdVod7hEcmD_F2QYUR8rNB271Zcob2elY')

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

zips = pd.read_csv('/Users/jennifer/Documents/cariboucity/sourcegis/myziplist.csv')
zips['zip code'] = zips['ZCTA5']


##############################################################


# conversion into data frame object
# now to go through the stores and extract the useful info
# most important is coords, next important - corp owned or licensed?
# equipment on site? is it a Reserve store? Drive through?
# CO - corporate store, LS - licensed store

# zips it won't geocode: 55001, 55032, 55029, 55031, 55085, 55054, 55339, 55366, 56313, 56363, 56028, 54007, 54010, 54014

zipframe = [zipFrame(i)for i in zips['zip code']]
 

datadir = '/Users/jennifer/Documents/cariboucity/scrapers/data/'

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

# renaming some columns
biglist = biglist.rename(columns={'coordinates.latitude': 'latitude', 'coordinates.longitude':'longitude',
                                  'ownershipTypeCode':'ownership', 'address.streetAddressLine1':'address',
                                  'address.city':'city'})
# selecting only columns of interest
biglist = biglist[['id', 'city', 'address', 'zip code', 'latitude', 'longitude', 'features', 'name', 'ownership', 'storeNumber']]

# enumerating the features into categorical variables
for i in range(0, len(biglist['features'])):
   biglist['features'][i] = eval(str(biglist['features'][i]))
   for j in range(0, len(biglist['features'][i])):
       namely = (biglist['features'][i][j]['name'])
       # checks if this feature has been reported yet at a local store
       if namely in biglist:
           biglist[namely][i] = 1
       # creates column for the feature if it hasn't been seen yet
       else:
           biglist[namely]=0
           biglist[namely][i] = 1

# I know from EDA that there are some stores with incorrect coordinates on the
# Starbucks website. If those stores are in my file, I will correct them
           
biglist.loc[biglist['id']==1020164]['latitude'] = 44.948911
biglist.loc[biglist['id']==1020164]['longitude'] = -93.296083
biglist.loc[biglist['id']==1022964]['latitude'] = 45.019007
biglist.loc[biglist['id']==1022964]['longitude'] = -93.325700
biglist.loc[biglist['id']==1022984]['latitude'] = 45.019689
biglist.loc[biglist['id']==1022984]['longitude'] = -93.327546

import datetime
biglist = biglist.drop(['features'], axis=1)
biglist.to_csv(datadir+ "twincitysbux" + str(datetime.date.today()) + ".csv", index = False)
