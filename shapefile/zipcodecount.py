import pandas as pd

import geopandas as gpd

# reading the shapefile of Twin Cities zipcodes
# and the calculated number of stores in each zip
zipshape = gpd.read_file('~/data/zipcodes/Census2000TigerZipCodeTabAreas.shp')
# reading in the store and count data from the parser files
zipcaribou = pd.read_csv('`/data/cariboucount.csv')
zipstarbucks = pd.read_csv('/Users/jennifer/Documents/starbucks/data/starbuckscount.csv')
# editing column name
zipcaribou = zipcaribou.rename(columns={'count': 'Caribou stores'})
zipstarbucks = zipstarbucks.rename(columns={'count': 'Starbucks stores'})

# the goal here is to add the info contained in zipcaribou and zipstarbucks into zipshape
# making sure column name matches
zipshape = zipshape.rename(columns={'ZCTA': 'zip code'})
# making sure column type is the same
zipcaribou['zip code'] = zipcaribou['zip code'].astype(unicode)
zipstarbucks['zip code'] = zipstarbucks['zip code'].astype(unicode)
zipshape = zipshape.merge(zipcaribou, on='zip code')
zipshape = zipshape.merge(zipstarbucks, on='zip code')
# exporting back to shapefile
zipshape.to_file('/Users/jennifer/Documents/starbucks/data/zipcodes/Census2000ZipsStoreCounts.shp')
