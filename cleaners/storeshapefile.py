
import pandas as pd

# reading in the scraped store data
star = pd.read_csv('~/Documents/cariboucity/scrapers/data/twincitysbux.csv')
bou = pd.read_csv('~/Documents/cariboucity/scrapers/data/twincitycaribou.csv')


# I want to join the data from both stores into one frame that has store name (Caribou or Starbucks), store id, and coordinates
# this is the data I will eventually use for ML, but also for Tableau and visualization.
# Becauze ZCTA and USPS zip code do not 100% match, and website has potential for misentered data,
# I will use GIS to create a new zip code column based on polygon where lat and long point lies

# note I want to work in projection NA83 / UTM zone 15N
# aka EPSG: 26915
# easier to transform a few hundred points than a hundred multipolygons!

# first, I'm making sure each row states whether it is Caribou or Starbucks by creating a 'brand' column
bou['brand'] = 'Caribou'
star['brand'] = 'Starbucks'
# combining all stores into one table, and deleting the two separate tables
both = bou.append(star)
del(bou, star)
# keeping the brand, latitude, longitude, id, and city information
both = both[['brand', 'latitude', 'longitude', 'id', 'city']]
both.index = (range(len(both)))
# exporting to csv archive
both.to_csv('~/Documents/cariboucity/scrapers/data/cleanstores.csv')

# now to begin the GIS work of finding each store's zip code / ZCTA
# must make the data from the 'both' frame into a dictionary for use w Shapely and Fiona
storepoints = both.to_dict(orient = 'records')
# adding point info to each store in storepoints
from shapely.geometry import Point
# pyporj library handles projections
import pyproj
# oldProj is the projection of the Google web service
oldProj = pyproj.Proj(init='epsg:3857')
# newProj is the GIS projection of the Census shapefiles
newProj = pyproj.Proj(init='epsg:26915')

for row in storepoints:
    # adding point info to each store in storepoints
    # first making sure projection is correct
    x0, y0 = oldProj(float(row['longitude']), float(row['latitude']))
    x1, y1 = pyproj.transform(oldProj, newProj, x0, y0)
    row['point'] = Point(x1, y1)
# now to read in the shapefile of ZCTAs created with 'countyfips.py'
# we want to add zip code info for each store based in what zip code polygon it's coords fall into

# first reading zip code shapefile with fiona
import fiona
zipframe = fiona.open("~/Documents/cariboucity/sourcegis/edited/tczips/census2010zips.shp",'r')
zipshape = range(len(zipframe))
# converting each polygon/multipolygon from zipshape to a shapely polygon
from shapely.geometry import shape
for i in(range(len(zipframe))):
    zipshape[i] = shape(zipframe[i]['geometry'])

'''

# going through each point and seeing where it falls within a polygon
# id 34 and 42 and 55 are a single polygon each
     # point 78 should fall in polygon 55
# id 3 is a multipolygon
     
There are 410 stores and only 185 shapefiles/zip codes
Each store has a zip, but not every zip has a store
'''
for i in range(len(storepoints)):
    storepoints[i]['zip code'] = 'NaN'
    for j in range(len(zipshape)):
        if zipshape[j].contains(storepoints[i]['point']) == True:
            storepoints[i]['zip code'] = str(zipframe[j]['properties']['ZCTA5'])

# just want stores that fall within a ZCTA
# turning back to a pandas df to filter out rows that don't have a zip code
storepoints = pd.DataFrame.from_dict(storepoints)
storepoints = storepoints[storepoints['zip code']!= 'NaN']
# back to a list for further geoprocessing
storepoints = storepoints.to_dict(orient = 'records')

'''

# writing the points to a shapefile
'''
from fiona import collection
from fiona.crs import from_epsg
from shapely.geometry import mapping, shape

schema1 = { 'geometry': 'Point', 'properties': { 'id': 'int' , 'brand': 'str', 'zip code': 'str','latitude': 'float', 'longitude': 'float', 'city': 'str'} }

with collection(
    "~/Documents/cariboucity/sourcegis/edited/tczips/myfiona", "w", "ESRI Shapefile", schema = schema1, crs = from_epsg(26915)) as output:
        for row in storepoints:
            # adding point info to each store in storepoints
            output.write({
                'geometry': mapping(row['point']),
                'properties': {
                    'id': row['id'],
                    'brand': row['brand'],
                    'zip code': row['zip code'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'city': row['city']
                }
            })
