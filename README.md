# Coffee in the Cities: Analysis of the Battleground between Caribou, Dunn Brothers, and Starbucks

## Introduction
Coffee shops are an occasional treat for some, but an important daily ritual for others. Catering to students, professionals, travelers, and more alike with comfortable seating and warm ambiance, there are plenty of options for those who want a sip prepared for them throughout the Twin Cities. Two players in particular have a formidable presence in the metro: Caribou Coffee and Starbucks Coffee, with Dunn Brothers a close third. My goals with this project are to:

1. Collect store location data for all three brands

2. Examine what characteristics are typical for a neighborhood with at least one of the chain coffee shops present

3. Predict where new stores may be opened

4. Determine if there is a difference between the brands' locations, and subsequently customers

![Map of Minneapolis area coffee shops](https://github.com/jlweichen/Coffee-in-the-Cities/blob/combo/thirdmap.png)

### Caribou Coffee
<details>
This chain opened its first shop in Edina on December 14, 1992 - by the way, it's still there at 44th and France. Today, Caribou Coffee still has a huge presence in the Twin Cities in spite of its current owner, JAB Holding Company, having majority interest in other coffee chains as well. Caribou's headquarters is located in Brooklyn Center, and even has a storefront open to the public!


If you need proof of the chain's proliferation in the area, <a href= "https://locations.cariboucoffee.com/us">there are five stores at Mall of America</a>. However, good luck finding a Caribou while wandering outside the Cities. There are a smattering of locations on the East Coast, mainly in popular Southern cities, but Caribou Coffee is unknown in the Mid-Atlantic and New England states. International presence is <a href = 'https://www.cariboucoffee.com/locations/around-the-world?ssl=true'>limited to Asia, Africa, and the Middle East</a>. Some locations are found in supermarkets such as local chain Lunds & Byerlys. <a href = 'https://www.cariboucoffee.com/corporate-folder/our-company/company-info'>More info about Caribou Coffee can be found here</a>.
</details>

### Starbucks Coffee
<details>
Known worldwide, Starbucks is the home of Pike Place Roast and the originator of the Pumpkin Spice Latte. Whether you are in the United States or abroad, Starbucks locations are ubiquitous, and even the Twin Cities have their fair share - but in terms of number of locations, they are second to Caribou.

In addition to corporate-owned stores, many Starbucks coffee shops are licensed. Of note is that Target, headquartered in Minneapolis, <a href = 'https://progressivegrocer.com/dow-jones-target-plans-put-starbucks-coffee-shops-its-stores'>has agreed with Starbucks to open a licensed location in each new Target store since 2002</a>. For the sake of this analysis I will not differentiate between corporate and licensed stores. <a href = 'https://www.starbucks.com/about-us/company-information'>More info about Starbucks Coffee can be found here</a>.
</details>

## Data
<details>
I used three main sources of data for this analysis. For the <a href = 'https://locations.cariboucoffee.com/'>Caribou Coffee</a> and <a href ='https://www.starbucks.com/store-locator'>Starbucks Coffee</a> locations, I used their respective websites. For the demographic Census data, I used files provided by the <a href='https://metrocouncil.org/Data-and-Maps.aspx'>Metropolitan Council</a> and Minnesota Geospatial Information Office, made available for download through the <a href='https://gisdata.mn.gov'>Minnesota Geospatial Commons</a>. Specifically, I used the <a href = 'https://gisdata.mn.gov/dataset/us-mn-state-metc-society-census-acs'>cleaned American Community Survey 5-Year Summary File</a> provided by the Metro Council, containing the 2013-2017 five-year ACS estimates for more insight on each zip code's population and demographics. For the zip code and block group shapefiles, I downloaded the Census <a href = 'https://gisdata.mn.gov/dataset/bdry-zip-code-tabulation-areas'>TIGER shapefile</a> for Minnesota zip codes, provided by the Minnesota Geospatial Information Office. I limited my analysis to zip code tabulated areas (ZCTAs) which either wholly or partially fall into one of the seven counties covered by the Metropolitan Council - Anoka, Carver, Dakota, Hennepin, Ramsey, Scott, and Washington.
</details>

## Methodology

### Overall Workflow
<details>
1. Download geographic data: 
 - Census.gov for the ZCTA shapefile, Census block shapefiles, ZCTA to county/state flat file, LODES data
 - Metropolitan Council for the ACS five year summary data
2. Run zipcodes.py to create list of zip codes and a shapefile containing the outline of each zip code tabulated area (ZCTA) of interest, which would be those in the MSA counties (data changes infrequently - the Census ZCTA shapefiles used for ACS are only updated for the decennial Census, and the MSA was last redefined in 2013)
3. Run censusmetroblockgroups.py, which does a similar task but for the census block groups in the seven county area.
4. Run dataprepper.py, which collects the approximately 10 (Caribou) or 50 (Starbucks) closest stores to each zip code, archives store info, and merges store data with Census data to create two shapefiles and one CSV (data changes frequently - stores close, open, move, etc. Starbucks regularly closes stores for remodeling - these stores don't show up when searching the site.)
5. Use the shapefiles created with dataprepper.py to perform exploratory data anlysis in Tableau
6. Use the csv created with dataprepper.py for machine learning
7. Create a list of census blocks or ZCTAs which the ML methods indicate are characteristic of those with at least one coffee shop, but do not currently have any
</details>

### Step 1: Prepping
<details>
Prior to collecting store data, I made sure I had shapefiles covering the entire seven-county area of interest, as well as Census data at the levels of ZCTA, block group, and block. I also checked the websites of each store to analyze the structure of the HTML output of store location data.
</details>

### Step 2: Scraping
<details>
The store data was scraped from each store's Store Locator page. I wrote three Python modules which parsed the store locator results for each zip code in the metro via BeautifulSoup, and aggregated them into a Pandas dataframe. These scraper modules can be found at https://github.com/jlweichen/Coffee-in-the-Cities/tree/master/scrapers. For the Starbucks scraper, I utilized the <a href = 'https://developers.google.com/maps/documentation/geocoding/intro'>Google Maps API, specifically the geocode utility</a>, to approximate each zip code as a pair of latitude and longitude coordinates. To use the code as-is, you will need a Google Maps API key. The modules create three data frames and date-stamped CSV files with point location data - one for Caribou, one for Dunn Brothers, and one for Starbucks.
</details>

### Step 3: Exploratory Analysis - First Round
<details>
I exported the CSV files into QGis and Tableau for exploratory analysis. I joined this data with the ACS and shapefile data to get a cursory glance. Some stores fell on the outer periphery of the search area, and I used QGis's "Clip" function to curtail my analysis only to those stores that fell within one of the zip code areas of interest. I also used QGis to convert my clipped CSV files into shapefiles, which I was able to import into Tableau. With Tableau, I was able to perform more visual analysis, especially with regards to numerical calculations, though initially I had trouble joining the shape files since the ACS shapefile had zip codes formatted as Unicode strings, while the point location shapefiles QGis created set the zip code column to integer by default. Tableau wouldn't join the columns because they were different data types. Using QGis and Tableau also helped me see where my data sets needed cleaning.
 </details>

### Step 3a: Cleaning Data
<details>
In QGis and Tableau, I originally joined the store data to the zip code shapefile by the zip code of the store's mailing address. In at least one case, the point location's coordinates fell outside of or adjacent to the boundaries of its' mailing address zip code. In some cases, like a Starbucks in St. Paul with a Minneapolis zip code, this was due to a data error. In other cases, typically those on the edge of a zip code area, it is likely due to the difference between the Census defined ZCTA and the zip codes as assigned by the USPS. I originally wanted to use the zip codes as defined by the stores themselves, but due to the number of discrepancies between store mailing zip codes and the ZCTAs in which stores fell, I decided to analyze stores by the ZCTA in which they were located. This required QGis to join the point shapefile to the ZCTA shapefile.

Finally, I had to make sure my zip code data was properly formatted in QGis before attempting to use it in Tableau. By default, QGis converted my zip code data from Unicode to integer. I had to use the "Refactor fields" geoprocessing tool to make sure my zip codes were considered strings before saving my shapefiles.
</details>

### Step 3b: Exploratory Analysis - Second Round
<details>
With clean, formatted data I was able to return to Tableau and join my three data sets - the Census data, the Caribou Coffee data, and the Starbucks data. I've begun making some nice visualizations in Tableau, which can be found here:

https://public.tableau.com/profile/jennifer5948#!/vizhome/coffeecities/CoffeeintheCities

This is a workbook in progress, but I've begun making some visualizations. Of note:
1. There are 210 Caribou Coffee shops in the area of interest, and only 171 Starbucks Coffee shops.
2. Downtown Minneapolis (55402) has the most coffee shops total (14), with suburban Woodbury (55125) right behind it (12).
3. The Caribou-only zip codes with the most stores are 55303 in Oak Grove and 55101 in downtown St. Paul, with 4 Caribou and 0 Starbucks.
4. The Starbucks-only zip code with the most stores is 55104 in St. Paul, with 3 Starbucks and 0 Caribou.
5. The two closest-together Starbucks are both at the new Hy-Vee in Robbinsdale. One is a drive-thru store and one is within the grocery store. They are only about 575 feet apart!
</details>

### Step 4: Machine Learning
<details>
Some ideas for using ML with this data:
1. Predicting the number of coffee shops in a given zip code based on ACS data
2. Modelling the coverage of Caribou stores vs Starbucks nearest-neighbor
3. Given a lat and long pair, determine whether a store location built there will be a Starbucks or Caribou store
4. Finding zip codes that may offer opportunity to open a new store / underserved markets
</details>
