# The purpose of this file is to take a shapefile of Census block groups for
# Minnesota, and extract the polygons that lie in a county considered part of the Twin Cities Metropolitan Council.

import pandas as pd
import geopandas as gpd
import fiona

from shapely.geometry import shape, polygon
# The name of the directory where most data will be read and written
datadir = '/Users/jennifer/Documents/cariboucity/sourcegis/'

# have to read in the state shapefile from the Census

# taking only the Minnesota blocks (state FIPS 27)

# COUNTYFP is the field of interest in the shapefile
# we only want polygons where COUNTYFP matches a county in the metro

minnesota = gpd.read_file('/Users/jennifer/Documents/GIS/GIS data/TIGER/tl_2018_27_bg/tl_2018_27_bg.shp')
minnesota.crs = {'init': 'epsg:4269'}
# then filter just for the counties we want
mncounties = pd.DataFrame({'County Name': ['Anoka', 'Carver', 'Dakota', 'Hennepin',
                                    'Ramsey', 'Scott', 'Washington'],
                           'COUNTYFP': ['003', '019', '037', '053', '123', '139', '163']})

mnfips = minnesota.merge(mncounties, on='COUNTYFP', how='inner')


# making sure index is nice and clean
mnfips.index = range(0, len(mnfips))

# removing columns that aren't of interest
mnfips = mnfips.drop(['STATEFP', 'COUNTYFP', 'TRACTCE', 'NAMELSAD', 'BLKGRPCE',
                  'MTFCC', 'FUNCSTAT', 'INTPTLAT', 
                  'INTPTLON'], axis=1)
mnfips = mnfips.rename(columns={'GEOID': 'BLOCK GROUP'})
# projection of outgoing shapefile
# want to change from EPSG 4269 to EPSG 26915
# running both.crs in the console will show EPSG 4269 is the current projection
# changing projection to NAD83 / UTM zone 15N

mnfips = mnfips.to_crs({'init': 'epsg:26915'})
# writing shapefile with just the blocks - no data added yet
# will do that in a different script refresh.py
mnfips.to_file(datadir + 'edited/tcblockgroups/base/twincitiesmetroblockgroups.shp')
