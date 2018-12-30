# The purpose of this file is to take a shapefile of ZCTAs for Minnesota
# and extract the zip codes that lie (either wholly or partially) in a county
# considered part of the Twin Cities metropolitan area

import pandas as pd
import geopandas as gpd

# name of directory where most data will be read and written
datadir = '~/Documents/cariboucity/sourcegis/'

# reading in a copy of Census csv saved to disk
# to match ZCTA to county
fun = pd.read_csv(str(datadir+ 'zctatocounty.csv'), dtype={'ZCTA5': 'unicode'})
# taking only the Minnesota (state number 27)counties from this lengthy file
minnesota = fun[fun['STATE']==27]
del(fun)

# counties of interest - Anoka, Carver, Dakota, Hennepin, Ramsey, Scott, Washington
# FIPS for these are 003, 019, 037, 053, 123, 139, 163
counties = pd.DataFrame({'Name': ['Anoka', 'Carver', 'Dakota', 'Hennepin', 'Ramsey', 'Scott', 'Washington'], 'COUNTY': [3, 19, 37, 53, 123, 139, 163]})
metrofips = minnesota.merge(counties, on='COUNTY', how='inner')
metrofips = metrofips.drop_duplicates()
fipsofinterest = metrofips[['ZCTA5']].drop_duplicates()
metrofips['ZCTA5'] = metrofips['ZCTA5'].astype('unicode')

# taking the zips of interest from a locally saved copy of shapefile:
# ZIP Code Tabulation Areas, 5-digit (ZCTA5), Minnesota, 2010
# acquired from the state GIS site
zipshape = gpd.read_file(datadir+'raw/mn_zip_code_tabulation_areas/zip_code_tabulation_areas.shp')
zipshape = zipshape.rename(columns = {'ZCTA5CE10': 'ZCTA5'})
somezips = zipshape.merge(metrofips, on = 'ZCTA5', how = 'right')
somezips.to_file(datadir+'edited/tczips/census2010zips.shp')
