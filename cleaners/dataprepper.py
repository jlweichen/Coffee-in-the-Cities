#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# My goal: to read store data, trim only to those stores within a census
# block group of interest, spit out two shapefiles:
# one with store point location data, and one with block group polygons

# first read in some useful libraries
import datetime
import sys
# modules I wrote for reading in the scraped store data
sys.path.append('~/cariboucity/scrapers')
import sbuxscraper
import caribouscraper
# data science libraries
import pandas as pd
import numpy as np
# GIS libraries
import geopandas as gpd
from shapely.geometry import Point, shape, mapping
import pyproj
import fiona
from fiona import collection

# combining all stores into one table, and deleting the two separate tables
both = sbuxscraper.starFrame().append(caribouscraper.bouFrame())
# for this project I am not using store features
both = both[['id', 'brand', 'latitude', 'longitude', 'address', 'city']]
both.index = range(len(both))

# must make the data from the 'both' frame into a list of dictionaries for use 
# with Shapely and Fiona, which work better with something resembling GeoJSON
storepoints = both.to_dict(orient = 'records')
# oldProj is the projection of the Google web service - how our scraped data was projected
oldProj = pyproj.Proj(init='epsg:3857')
# newProj is the GIS projection of the Census shapefiles, which we edited in countyfips.py
newProj = pyproj.Proj(init='epsg:26915')

def reProjection(row):
    global oldProj, newProj
    x0, y0 = oldProj(float(row['longitude']), float(row['latitude']))
    x1, y1 = pyproj.transform(oldProj, newProj, x0, y0)
    row['point'] = Point(x1, y1)
    return
map(reProjection, storepoints)

# now to read in the shapefile of Metro Census block groups
# we want to add block group info for a store, based on the polygon it's coords fall into
# https://automating-gis-processes.github.io/2016/Lesson3-point-in-polygon.html#how-to-check-if-point-is-inside-a-polygon
# first reading block group shapefile with fiona
# there are 2,086 block groups between all seven counties
block = fiona.open("~/cariboucity/sourcegis/edited/tcblockgroups/base/twincitiesmetroblockgroups.shp",'r')
blockshapes = map(lambda x: shape(x['geometry']), block)
blockfeatures = map(lambda x: (x['properties']), block)

blocks = pd.DataFrame(blockfeatures).join(pd.DataFrame(blockshapes, columns = ['geometry']))
blocks = blocks.rename(columns={'BLOCK GROU': 'Block Group'})

# going through each point and seeing where it falls within a polygon
# stores on the periphery likely won't fall within a Census block polygon

for i in range(len(storepoints)):
    storepoints[i]['Block Group'] = False
    for j in range(len(blocks.index)):
        if blocks['geometry'][j].contains(storepoints[i]['point']) == True:
            storepoints[i]['Block Group'] = str(blocks['Block Group'][j])

# dropping stores outside of the Metropolitan Council area
# approx. 369 total coffee shops
# Caribou typically has 205 and Starbucks around 164 but stores close for "refresh"
            
storepoints = filter(lambda x: bool(x['Block Group']),storepoints)

# writing the points to their own shapefile

schema1 = { 'geometry': 'Point', 'properties': { 'id': 'str' , 'brand': 'str', 'Block Group': 'str',
            'latitude': 'float', 'longitude': 'float', 'address': 'str','city': 'str'} }
with collection(
    "~/cariboucity/sourcegis/edited/stores/metrostores"+ str(datetime.date.today()), 
    "w", "ESRI Shapefile", schema = schema1, crs = "+proj=utm +zone=15 +ellps=GRS80 +datum=NAD83 +units=m +no_defs" ) as output:
        for row in storepoints:
            # adding point info to each store in storepoints
            output.write({
                'geometry': mapping(row['point']),
                'properties': {
                    'id': row['id'],
                    'brand': row['brand'],
                    'Block Group': row['Block Group'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'address': row['address'],
                    'city': row['city']
                }
            })
    
# converting back to a dataframe
storepoints = pd.DataFrame(storepoints)

# writing a function that uses the Shapely .contains() method for polygons
# to add store count for each block group
def caffeine(x):
    runs = [x.contains(y) for y in storepoints['point']]
    return sum(runs)
blocks['Coffee'] = blocks['geometry'].apply(caffeine)

# ACS 5 year summary data broken down by block group - a tract contains one or more block
# groups, each of which contain one or more blocks.
# This file is compiled and published by the Metropolitan Council, and includes
# counties outside of its 7-county jurisdiction.
# Metadata can be found at:
# ftp://ftp.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_metc/society_census_acs/metadata/metadata.html

acs = pd.read_excel('~/cariboucity/sourcegis/raw/xlsx_society_census_acs20132017/CensusACSBlockGroup.xlsx',
                    dtype = {'GEOG_UNIT':'unicode'})
acs = acs.rename(columns={'GEOG_UNIT': 'Block Group'})
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

blocks=blocks.merge(acs, on='Block Group', how = 'inner')

# Let's bring in the Census LODES data.
# Workplace Area Characteristics would probably be useful - don't people drink coffee at work?
# Our data is from 2015, and covers all jobs. Data from other years and job segments
# are also available online.
# I'm using the WAC datasets from 2015 for Minnesota and Wisconsin

MNlodes = pd.read_csv('~/GIS/GIS data/LODES/mn_wac_S000_JT00_2015.csv')
MNlodes.index = range(0, len(MNlodes))

# see https://lehd.ces.census.gov/data/lodes/LODES7/LODESTechDoc7.3.pdf
# provides summary of the data table - each row is a Census block

# I am choosing to drop some columns, mostly ones regarding worker race and the
# age of the employing firm
MNlodes= MNlodes.drop(['CFA01', 'CFA02', 'CFA03', 'CFA04', 'CFA05', 'CFS01', 
                           'CFS02', 'CFS03', 'CFS04', 'CFS05', 'CR01', 'CR02',
                           'CR03', 'CR04', 'CR05', 'CR07', 'CT01', 'CT02', 'createdate'], axis=1)
# renaming some other columns so they are less confusing, and can be joined to other data
MNlodes = MNlodes.rename(columns={'w_geocode': 'GEOID10', 'C000': 'Total jobs'})

# GEOID10 column of the block shapefile needs to be joined with the w_geocode
# column of the LODES flat files - rename and make sure it's of string type so it can be joined
MNlodes['GEOID10'] = MNlodes['GEOID10'].astype(str)
# need block group aggregate values of job counts
# first make a column with the block group value
MNlodes['Block Group'] = [i[0:12] for i in MNlodes['GEOID10']]
# recall the LODES data is by Census block, NOT Census block group!
# first I will aggregate and sum this data and make a table where each row is a block group
# and each column is the total jobs of a certain type in that block group
blockgrouptot = MNlodes.groupby('Block Group', as_index = False).sum()

# joining the block group aggregated data to the both table
blocks = blocks.merge(blockgrouptot, on = 'Block Group', how = 'left')

# replacing NA values with zero, for blocks without any jobs
blocks = blocks.fillna(0)

# converting to GeoDataFrame and writing shapefile
blocks = gpd.GeoDataFrame(blocks, geometry = 'geometry')
blocks.crs = "+proj=utm +zone=15 +ellps=GRS80 +datum=NAD83 +units=m +no_defs "
blocks.to_file('~/cariboucity/sourcegis/edited/tcblockgroups/twincitiesmetroblockgroupswstorecounts'+ str(datetime.date.today())+'.shp')

# writing machine learning data to csv - this is the data that will be fed into ML
# no longer need block geometry, will drop that
blocks = blocks.drop(['geometry'], axis=1)
blocks.to_csv('~/cariboucity/ML/data/mlmetroblockgroup' + str(datetime.date.today())+'.csv', index = False)
