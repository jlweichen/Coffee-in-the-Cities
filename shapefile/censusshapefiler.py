import pandas as pd

import geopandas as gpd


'''
importing Census ACS data.
This is an Excel file, and has no projection info, shape info, etc.
Each row correlates to a disctinct ZCTA, or zip code tabulation area.
While not exactly the same as a Zip Code (as determined by USPS), they
are the same for all but a handful of Starbucks and Caribou stores
'''
census = pd.read_excel('~/data/xlsx_society_census_acs/CensusACSZipCode.xlsx')

census = census.rename(columns={'GEOG_UNIT': 'zip code'})
census['zip code'] = census['zip code'].astype(unicode)

'''
reading the shapefile of Twin Cities zipcodes
and the calculated number of stores in each zip
'''
zipshape = gpd.read_file('~/data/zipcodes/original/Census2000TigerZipCodeTabAreas.shp')
zipcaribou = pd.read_csv('~/data/cariboucount.csv')
zipcaribou = zipcaribou.rename(columns={'count': 'Caribou stores'})
zipstarbucks = pd.read_csv('~/data/starbuckscount.csv')
zipstarbucks = zipstarbucks.rename(columns={'count': 'Starbucks stores'})
# the goal here is to add the info contained in zipcaribou and zipstarbucks into zipshape
# making sure column name matches
zipshape = zipshape.rename(columns={'ZCTA': 'zip code'})
# making a unique number for each polygon
zipshape['number'] = range(0, len(zipshape['zip code']))
# making sure column type is the same for each store count zip code column
zipcaribou['zip code'] = zipcaribou['zip code'].astype(unicode)
zipstarbucks['zip code'] = zipstarbucks['zip code'].astype(unicode)
# best way is a right join with zipshape on the right
# but resulting frame won't be a geopandas frame
# so to keep it a geopandas frame, will be a bit convoluted

somezips = zipshape[['zip code']]
somezips = somezips.merge(census, on = 'zip code', how = 'left')

somezips = somezips.merge(zipcaribou, on = 'zip code', how='left')
somezips = somezips.merge(zipstarbucks, on= 'zip code', how='left')
somezips['delta'] = somezips['Caribou stores'] - somezips['Starbucks stores']
somezips['total'] = somezips['Caribou stores'] + somezips['Starbucks stores']
somezips['number'] = range(0, len(somezips['zip code']))

# left joining back to the original frame

zipshape = zipshape.merge(somezips, on='number')
# exporting back to shapefile

zipshape=zipshape.drop(['number', 'zip code_y'], axis=1)
zipshape = zipshape.rename(columns={'zip code_x': 'zip code'})

zipshape.to_file('~/data/zipcodes/edited/ACSCensus2000ZipsStoreCounts.shp')
