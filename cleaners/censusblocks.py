# The purpose of this file is to take two shapefiles of Census blocks - one for
# Minnesota, and one for Wisconsin - and extract the polygons that lie (either wholly
# or partially) in a county considered part of the Twin Cities metropolitan area
# by the Census. Then, it will add store presence data (binary yes/no) to each block.
# Finally, each block will be joined with its block group's data from the ACS 5-year estimates
# and the block's data from the LODES

import pandas as pd
import geopandas as gpd

# The name of the directory where most data will be read and written
datadir = '/Users/jennifer/Documents/cariboucity/sourcegis/'

# have to read in the state block shapefiles from the Census
# two files - one for Minnesota and one for Wisconsin -
# which contain all blocks within each state

# taking only the Minnesota blocks first (state FIPS 27)

# COUNTYFP10 is the field of interest in the shapefile
# we only want polygons where COUNTYFP10 matches a county in the metro
minnesota = gpd.read_file('/Users/jennifer/Documents/GIS/GIS data/TIGER/tl_2018_27_tabblock10/tl_2018_27_tabblock10.shp')
# then filter just for the counties we want
mncounties = pd.DataFrame({'County Name': ['Anoka', 'Carver','Chisago', 'Dakota', 'Hennepin',
                                    'Isanti', 'Le Sueur', 'Mille Lacs', 'Ramsey', 'Scott', 
                                    'Sherburne', 'Sibley', 'Washington', 'Wright'],
                           'COUNTYFP10': ['003', '019', '025', '037', '053', '059', '079', '095', '123', '139', '141', '143', '163', '171']})
mnfips = minnesota.merge(mncounties, on='COUNTYFP10', how='inner')

# same thing with Wisconsin state FIPS 55

wisconsin = gpd.read_file('/Users/jennifer/Documents/GIS/GIS data/TIGER/tl_2018_55_tabblock10/tl_2018_55_tabblock10.shp')
wicounties = pd.DataFrame({'County Name': ['Pierce', 'Saint Croix'],
                           'COUNTYFP10': ['093', '109']})
wifips = wisconsin.merge(wicounties, on='COUNTYFP10', how='inner')

# put them together - now we have all the Census blocks in the Twin Cities MSA
both = mnfips.append(wifips)             
del(minnesota, wisconsin, mncounties, wicounties, mnfips, wifips)

# making sure index is nice and clean
both.index = range(0, len(both))
# adding a column that has block group - will need later for ACS data
both['BLOCK GROUP'] = [i[0:12] for i in both['GEOID10']]
# removing columns that aren't of interest
both = both.drop(['STATEFP10', 'COUNTYFP10', 'TRACTCE10', 'BLOCKCE10', 'NAME10', 
                  'MTFCC10', 'FUNCSTAT10', 'ALAND10', 'AWATER10', 'INTPTLAT10', 
                  'INTPTLON10', 'UACE10', 'UATYPE'], axis=1)
# the column UR10 is a Census flag - is this block urban or rural?
# we can rename and clean this column - it may be valuable info
# let's call it Urban - value is 1 if the block is urban and 0 if it isn't
both = both.rename(columns = {'UR10': 'Urban'})
# if both['Urban'] is U, reassign it 1, or 0 if it is R
both['Urban'] = both['Urban'].apply(lambda x: 1 if x=='U' else 0)

# projection of outgoing shapefile
# want to change from EPSG 4269 to EPSG 26915
# running both.crs in the console will show EPSG 4269 is the current projection
# changing projection to NAD83 / UTM zone 15N
both = both.to_crs({'init': 'epsg:26915'})
# writing shapefile with just the blocks - no data added yet
both.to_file(datadir+ 'edited/tczips/twincitiesblocks.shp')
# reading in stores data, using the shapefile created with storeshapefile.py
stores = gpd.read_file("/Users/jennifer/Documents/cariboucity/sourcegis/edited/tczips/stores2018-12-31/stores2018-12-31.shp")

# creating storecount column in 'both' called 'Coffee'
# iterating through polygons of the Census blocks
# will flag 0 if no stores, 1 if there is a store
# very very few blocks have multiple stores less than 10 have three or more
# at the block level, better off doing some binary prediction like logistic regression

# writing a function that uses the Shapely .contains() method for polygons
def caffeine(x):
    runs = [x.contains(y) for y in stores['geometry']]
    if any(runs) == True:
        return 1
    else:
        return 0
# calling the function on the geometry column of the 'both' dataframe
both['Coffee'] = both['geometry'].apply(caffeine)

# writing to shapefile
both.to_file(datadir+ 'edited/tczips/twincitiesblockswithstorecounts.shp')

# no longer need block geometry, will drop that
both = both.drop(['geometry'], axis=1)
                
# ACS 5 year summary data broken down by block group - a tract contains one or more block
# groups, each of which contain one or more blocks.
# This file is compiled and published by the Metropolitan Council, and includes
# counties outside of its 7-county jurisdiction.
# Metadata can be found at:
# ftp://ftp.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_metc/society_census_acs/metadata/metadata.html

acs = pd.read_excel('/Users/jennifer/Documents/cariboucity/sourcegis/raw/xlsx_society_census_acs20132017/CensusACSBlockGroup.xlsx',
                    dtype = {'GEOG_UNIT':'unicode'})
acs = acs.rename(columns={'GEOG_UNIT': 'BLOCK GROUP'})
# dropping some columns, like those around citizenship, disability, language
# choosing not to use these in analysis - I'd prefer to look at age, income, housing,
# education, and race
acs = acs.drop(['GEOG_LEVEL', 'GEOID', 'BLKGRP', 'GEOID2', 'GEONAME', 'SUMLEV', 'COUNTY',
                'SOURCE', 'TRACT', 'GEOCOMP', 'YEAR', 'USBORNCIT', 'FORBORNCIT', 
                'FORBORNNOT', 'CDENOM', 'CDENOM_017', 'CDENOM_517', 'CDENOM1864', 
                'CDENOM65UP', 'ANYDIS', 'ANYDIS_017', 'ANYDIS1864', 'ANYDIS65UP', 
                'DEAF', 'DEAF_017', 'DEAF1864', 'DEAF65UP', 'VISION', 'VISION_017',
                'VISION1864', 'VISION65UP', 'COGDIS', 'COGDIS_517', 'COGDIS1864', 
                'COGDIS65UP', 'AMBDIS', 'AMBDIS_517','AMBDIS1864', 'AMBDIS65UP',
                'SELFCARE' , 'SELFCA_517', 'SELFCA1864', 'SELFCA65UP', 'INDLIV',
                'INDLIV_517', 'INDLIV1864', 'INDLIV65UP', 'ENGLISH', 'ESL_VWELL', 
                'LEP', 'LEP_SPAN', 'LEP_RUSS', 'LEP_CHIN','LEP_HMONG', 'LEP_VIET', 
                'LEP_AFRICA'], axis=1)

both=both.merge(acs, on='BLOCK GROUP', how = 'inner')

# Let's bring in the Census LODES data.
# Workplace Area Characteristics would probably be useful - don't people drink coffee at work?
# Our data is from 2015, and covers all jobs. Data from other years and job segments
# are also available online.
# I'm using the WAC datasets from 2015 for Minnesota and Wisconsin

MNlodes = pd.read_csv('/Users/jennifer/Documents/GIS/GIS data/LODES/mn_wac_S000_JT00_2015.csv')
WIlodes = pd.read_csv('/Users/jennifer/Documents/GIS/GIS data/LODES/wi_wac_S000_JT00_2015.csv')
bothlodes = MNlodes.append(WIlodes)
bothlodes.index = range(0, len(bothlodes))
# see https://lehd.ces.census.gov/data/lodes/LODES7/LODESTechDoc7.3.pdf
# provides summary of the data table - each row is a Census block

# I am choosing to drop some columns, mostly ones regarding worker race and the
# age of the employing firm
bothlodes= bothlodes.drop(['CFA01', 'CFA02', 'CFA03', 'CFA04', 'CFA05', 'CFS01', 
                           'CFS02', 'CFS03', 'CFS04', 'CFS05', 'CR01', 'CR02',
                           'CR03', 'CR04', 'CR05', 'CR07', 'CT01', 'CT02', 'createdate'], axis=1)
# renaming some other columns so they are less confusing, and can be joined to other data
bothlodes = bothlodes.rename(columns={'w_geocode': 'GEOID10', 'C000': 'Total jobs'})

# GEOID10 column of the block shapefile needs to be joined with the w_geocode
# column of the LODES flat files - rename and make sure it's of string type so it can be joined
bothlodes['GEOID10'] = bothlodes['GEOID10'].astype(str)

both = both.merge(bothlodes, on='GEOID10', how='left')
# replacing NA values with zero, for blocks without any jobs
both = both.fillna(0)
# renaming GEOID10 to Block Name
both = both.rename(columns = {'GEOID10': 'Block Name'})
# writing machine learning data to csv
both.to_csv('/Users/jennifer/Documents/cariboucity/ml.csv', index = False)
