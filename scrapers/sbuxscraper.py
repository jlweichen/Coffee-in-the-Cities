# this parses Starbucks website for location data

from bs4 import BeautifulSoup

import requests
import time
import googlemaps
import json

import pandas as pd
import datetime

datadir = '~/cariboucity/scrapers/data/'
##################################################
# authentication of Google Maps AI
gmaps = googlemaps.Client(key=xxxxxxxxxxxxxxxxxxxx)

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
    time.sleep(0.3)
    content = html.content
    return BeautifulSoup(content, 'html5lib')

# need coordinates and other data for each store
# this function needs work
# need <div id="bootstrapData"> where the coordinates are held
def storeFind(soup):
    pattern = re.compile(r'^\s*\bwindow.__BOOTSTRAP\b')
    addys = soup.body.find("script", text=pattern).text
#    need to cut everything after window.__INTL_MESSAGES
    addys2 = re.sub(r'^\s*\bwindow.__BOOTSTRAP\b\s\=\s', '', addys)
    addys3 = re.sub(r'\s+\bwindow.__INTL_MESSAGES\b.+\s+.+\s+', '', addys2)

    return json.loads(addys3)

def zipFrame(zip):
    try:
        soupy = soupify(zip)
        biglist = storeFind(soupy)
        stores = biglist['previousAction']['payload']['data']['stores']
        del(biglist)
        return pd.io.json.json_normalize(stores, errors = 'ignore')
    except:
        return
##############################################################    
# importing CSV of Twin Cities zip codes as a list

def zipper(path):
    zips = pd.read_csv(path, header = 0,  names = {'zip code'})
    return zips['zip code'].tolist()


##############################################################


# conversion into data frame object
# now to go through the stores and extract the useful info
# most important is coords, next important - corp owned or licensed?
# equipment on site? is it a Reserve store? Drive through?
# CO - corporate store, LS - licensed store

# zips it won't geocode: 55001, 55032, 55029, 55031, 55085, 55054, 55339, 55366, 56313, 56363, 56028, 54007, 54010, 54014
# zips: 55001, 55031, 55085, 55150, 55054
def bigFrame():
    zipframe = map(zipFrame, zipper('/Users/jennifer/Documents/cariboucity/sourcegis/myziplist.csv'))
    biglist = pd.concat(zipframe).rename(columns = {'address.postalCode': 'zip code',
                       'coordinates.latitude': 'latitude', 'coordinates.longitude':'longitude',
                       'ownershipTypeCode':'ownership', 'address.streetAddressLine1':'address',
                       'address.city':'city'})
    biglist = biglist.drop_duplicates('id')
    biglist['zip code'] = biglist['zip code'].apply(lambda x: x[0:5])
    biglist['address'] = biglist['address'].apply(lambda x: x.title())
    # cleaning capitalization on address data
    biglist['address'] = biglist['address'].apply(lambda x: re.sub('Mn', 'MN', x))
    # ensuring numerical streets are capitalized correctly
    def streetLower(match):
        return match.group(0).lower()
    def streetUpper(match):
        return match.group(0).upper()
    def abbreviator1(match):
        return match.group(0).replace(' ' , '. ')
    def abbreviator2(match):
        return match.group(0) + '.'
    def abbreviator3(match):
        return match.group(0).replace('.', '')
    biglist['address'] = biglist['address'].apply(lambda x: re.sub('(\d[A-Z])', streetLower, x))
    biglist['address'] = biglist['address'].apply(lambda x: re.sub('Ne | Ne$|Nw | Nw$|Se | Se$|Sw | Sw$|Sr', streetUpper, x))
    biglist['address'] = biglist['address'].apply(lambda x: re.sub(' S.| N.| E.| W.', abbreviator3, x))
    biglist['address'] = biglist['address'].apply(lambda x:
        re.sub('(St )|(Rd )|(Ave )|(Blvd )|(Dr )|(Av )|(Trl )|(Pkwy )|(Ctr )|(Ct )', abbreviator1, x))
    biglist['address'] = biglist['address'].apply(lambda x:
        re.sub('( St$)|( Rd$)|( Ave$)|( Blvd$)|( Dr$)|( Av$)|( Trl$)|( Pkwy$)|( Ctr$)|( Ct$)', abbreviator2, x))
    # street name spelling errors
    biglist['address'] = biglist['address'].apply(lambda x: re.sub('Gulmack', 'Glumack', x))
    biglist['address'] = biglist['address'].apply(lambda x: re.sub('Bonker', 'Bunker', x))
    # same for the city field
    biglist['city'] = biglist['city'].apply(lambda x: x.title())
    biglist['city'] = biglist['city'].apply(lambda x: re.sub('St ', abbreviator1, x))    
    biglist['brand'] = 'Starbucks'
    biglist.index = range(0, len(biglist))
    # I know from EDA that there are some stores with incorrect coordinates on the
    # Starbucks website. If those stores are in my file, I will correct them
           
    biglist.loc[biglist['id']=='1020164', 'latitude'] = 44.948911
    biglist.loc[biglist['id']=='1020164', 'longitude'] = -93.296083
    biglist.loc[biglist['id']=='1022964', 'latitude'] = 45.019007
    biglist.loc[biglist['id']=='1022964', 'longitude'] = -93.325700
    biglist.loc[biglist['id']=='1022984', 'latitude'] = 45.019689
    biglist.loc[biglist['id']=='1022984', 'longitude'] = -93.327546
    
    # cleaning city info for some stores
    biglist.loc[biglist['id']=='10142', 'city'] = 'Fridley'
    biglist.loc[biglist['id']=='11921', 'city'] = 'Crystal'
    biglist.loc[biglist['id']=='8387', 'city'] = 'Oakdale'
    biglist.loc[biglist['id']=='9656', 'city'] = 'Oak Park Heights'   
    biglist.loc[biglist['id']=='8480', 'city'] = 'West St. Paul'
    
    
    biglist = biglist[['brand', 'id', 'city', 'address', 'zip code', 'latitude',
                       'longitude', 'features', 'name', 'ownership', 'storeNumber']]
    return biglist

# parsing feature names 
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
        column[i] = eval(str(column[i]))
        for j in range(0, len(column[i])):
            feat = column[i][j]['name']
            namer(feat, i)
            print('store ' + str(i))      
    return

# cleaning city name data and returning a clean data frame

def starFrame():
    big = bigFrame()
    featurizer(big, 'features')
    big = big.drop(['features'], axis=1)
    # cleaning city name data

    goodcities = {'St.Paul': 'St. Paul', 'Saint Louis Park': 'St. Louis Park', 
                  'Saint Paul': 'St. Paul'}
    goodindex = goodcities.keys()

    for i in range(len(goodindex)):
        big['city'] = big['city'].replace(goodindex[i], goodcities[goodindex[i]])
    
    big.to_csv(datadir+ "twincitysbux" + str(datetime.date.today()) + ".csv", index = False)
    return big

