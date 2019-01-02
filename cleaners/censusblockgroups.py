# The purpose of this file is to take two shapefiles of Census block groups - one for
# Minnesota, and one for Wisconsin - and extract the polygons that lie (either wholly
# or partially) in a county considered part of the Twin Cities metropolitan area
# by the Census. Then, it will add store presence data (binary yes/no) to each block group.
# Finally, each block group will be joined with its block group's data from the
# ACS 5-year estimates and the LODES

import pandas as pd
import geopandas as gpd

# The name of the directory where most data will be read and written
datadir = '/Users/jennifer/Documents/cariboucity/sourcegis/'

# have to read in the state shapefiles from the Census
# two files - one for Minnesota and one for Wisconsin - each of
# which contain all block groups within the state

# taking only the Minnesota blocks first (state FIPS 27)

# COUNTYFP is the field of interest in the shapefile
# we only want polygons where COUNTYFP matches a county in the metro
minnesota = gpd.read_file('/Users/jennifer/Documents/GIS/GIS data/TIGER/tl_2018_27_bg/tl_2018_27_bg.shp')
# then filter just for the counties we want
mncounties = pd.DataFrame({'County Name': ['Anoka', 'Carver','Chisago', 'Dakota', 'Hennepin',
                                    'Isanti', 'Le Sueur', 'Mille Lacs', 'Ramsey', 'Scott', 
                                    'Sherburne', 'Sibley', 'Washington', 'Wright'],
                           'COUNTYFP': ['003', '019', '025', '037', '053', '059', '079', '095', '123', '139', '141', '143', '163', '171']})
mnfips = minnesota.merge(mncounties, on='COUNTYFP', how='inner')

# same thing with Wisconsin, whose state FIPS is 55

wisconsin = gpd.read_file('/Users/jennifer/Documents/GIS/GIS data/TIGER/tl_2018_55_bg/tl_2018_55_bg.shp')
wicounties = pd.DataFrame({'County Name': ['Pierce', 'Saint Croix'],
                           'COUNTYFP': ['093', '109']})
wifips = wisconsin.merge(wicounties, on='COUNTYFP', how='inner')

# put them together - now we have all the Census block groups in the Twin Cities MSA
both = mnfips.append(wifips)             
del(minnesota, wisconsin, mncounties, wicounties, mnfips, wifips)

# making sure index is nice and clean
both.index = range(0, len(both))

# removing columns that aren't of interest
both = both.drop(['STATEFP', 'COUNTYFP', 'TRACTCE', 'NAMELSAD', 'BLKGRPCE',
                  'MTFCC', 'FUNCSTAT', 'ALAND', 'AWATER', 'INTPTLAT', 
                  'INTPTLON'], axis=1)
both = both.rename(columns={'GEOID': 'BLOCK GROUP'})
# projection of outgoing shapefile
# want to change from EPSG 4269 to EPSG 26915
# running both.crs in the console will show EPSG 4269 is the current projection
# changing projection to NAD83 / UTM zone 15N
both = both.to_crs({'init': 'epsg:26915'})
# writing shapefile with just the blocks - no data added yet
both.to_file(datadir + 'edited/tcblockgroups/twincitiesblockgroups.shp')

# reading in stores data, using the shapefile created with storeshapefile.py
stores = gpd.read_file(datadir + "edited/tczips/stores2019-01-01/stores2019-01-01.shp")

# creating an indicator outcome column in 'both' called 'Coffee'
# iterating through polygons of the Census block groups
# will flag 0 if no stores, 1 if there is a store
# very very few block groups have multiple stores 


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
both.to_file(datadir+ 'edited/tcblockgroups/twincitiesblockgroupswithstorecounts.shp')

# 2,370 block groups of interest to us

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
del(MNlodes, WIlodes)
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
# need block group aggregate values of job counts
# first make a column with the block group value
bothlodes['BLOCK GROUP'] = [i[0:12] for i in bothlodes['GEOID10']]

# there are 8,540 block groups covering two states within my data
# I only need 2,370 of them
# first I will aggregate and sum this data and make a table where each row is a block group
# and each column is the total jobs of a certain type in that block group
blockgrouptot = bothlodes.groupby('BLOCK GROUP', as_index = False).sum()

# joining the block group aggregated data to the both table
both = both.merge(blockgrouptot, on = 'BLOCK GROUP', how = 'left')

# replacing NA values with zero, for blocks without any jobs
both = both.fillna(0)


# writing machine learning data to csv
import datetime
both.to_csv('/Users/jennifer/Documents/cariboucity/cleaners/data/mlblockgroup' + str(datetime.date.today())+'.csv', index = False)
