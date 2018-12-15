# Coffee in the Cities: Analysis of the Battleground between Caribou Coffee and Starbucks

## Introduction
Though I personally don't drink much coffee, it isn't hard to find someone who does. Coffee shops are an occasional treat for some, but are an important daily ritual for others. They cater to students, professionals, travelers, and more alike with comfortable seating and warm ambiance. There are plenty of options for those who want a sip prepared for them on their way to work, school, or errands throughout the Twin Cities, but two players have a formidable presence: Caribou Coffee and Starbucks Coffee. My goals with this project are to:

1. Collect store location data for both brands

2. Examine what characteristics are typical for a neighborhood with at least one of the chain coffee shops present

3. Predict where new stores may be opened

4. Determine if there is a difference between Starbucks and Caribou neighborhoods, and subsequently customers

### Caribou Coffee
This chain opened its first shop in Edina on December 14, 1992 - by the way, it's still there on 44th and France. Today, Caribou Coffee still has a huge presence in the Twin Cities in spite of its current owner, JAB Holding Company, having majority interest in other coffee chains as well. Caribou's headquarters in Brooklyn Center has a storefront open to the public.

If you need proof of the chain's proliferation in the area, there are five stores at the Mall of America alone! <a href= "https://locations.cariboucoffee.com/us">However, good luck finding them elsewhere</a>. There are a smattering of locations on the East Coast, mainly in popular Southern cities, but Caribou Coffee is unknown in the Mid-Atlantic and New England states. International presence is <a href = 'https://www.cariboucoffee.com/locations/around-the-world?ssl=true'>limited to Asia, Africa, and the Middle East</a>. Some locations are licensed, while others are corporate-owned, but I will not break down ownership in my analysis. <a href = 'https://www.cariboucoffee.com/corporate-folder/our-company/company-info'>More info about Caribou Coffee can be found here</a>.

### Starbucks Coffee
Known worldwide, Starbucks is the home of Pike Place Roast and the originator of the Pumpkin Spice Latte. Whether you are in the United States or abroad, Starbucks locations are ubiquitous, and the Twin Cities have their fair share.

In addition to corporate-owned stores, many Starbucks coffee shops are licensed. Of note is that Target, headquartered in Minneapolis, <a href = 'https://progressivegrocer.com/dow-jones-target-plans-put-starbucks-coffee-shops-its-stores'>has agreed with Starbucks to open a licensed location in each new Target store since 2002</a>. For the sake of this analysis I will not differentiate between corporate and licensed stores, but in a future Starbucks-specific analysis, I may. <a href = 'https://www.starbucks.com/about-us/company-information'>More info about Starbucks Coffee can be found here</a>.

## Data
I used three main sources of data for this analysis. For the <a href = 'https://locations.cariboucoffee.com/'>Caribou Coffee</a> and <a href ='https://www.starbucks.com/store-locator'>Starbucks Coffee</a> locations, I used their respective websites. For the demographic Census data, I used files provided by the <a href='https://metrocouncil.org/Data-and-Maps.aspx'>Metropolitan Council</a> and Minnesota Geospatial Information Office, made available for download through the <a href='https://gisdata.mn.gov'>Minnesota Geospatial Commons</a>. Specifically, I used the <a href = 'https://gisdata.mn.gov/dataset/us-mn-state-metc-society-census-acs'>cleaned American Community Survey 5-Year Summary File</a> provided by the Metro Council, containing the 2013-2017 five-year ACS estimates for more insight on each zip code's population and demographics. For the zip code shapefiles, I downloaded the Census <a href = 'https://gisdata.mn.gov/dataset/bdry-zip-code-tabulation-areas'>TIGER shapefile</a> for Minnesota zip codes, provided by the Minnesota Geospatial Information Office. I limited my analysis to zip code tabulated areas (ZCTAs) which either wholly or partially fall into one of the seven counties considered by the Metropolitan Council - Anoka, Hennepin, Ramsey, Washington, Scott, Dakota, and Carver. Some of these zip codes bleed over into adjacent Minnesota counties, such as Rice County, but none of them cross the river into Wisconsin. This is why some nearby stores in Hudson, WI are not included in this analysis while some Northfield, MN stores are.

## Methodology

### Step 1: Scraping
The store data was scraped from each store's Store Locator page. I used Python scripts which parsed the store locator results for each zip code in the metro via BeautifulSoup, and aggregated them into a Pandas dataframe. These scrapers can be found at https://github.com/jlweichen/Coffee-in-the-Cities/tree/master/scrapers. For the Starbucks scraper, I utilized the <a href = 'https://developers.google.com/maps/documentation/geocoding/intro'>Google Maps API, specifically the geocode utility</a>, to approximate each zip code as a pair of latitude and longitude coordinates. To use the code as-is, you will need a Google Maps API key. I created two CSV files with point location data - one for Caribou and one for Starbucks. I also collected zip code information for each store.

### Step 2: Exploratory Analysis - First Round
I exported the CSV files into QGis and Tableau for exploratory analysis. I joined this data with the ACS and shapefile data to get a cursory glance. Some stores fell on the outer periphery of the search area, and I used QGis's "Clip" function to curtail my analysis only to those stores that fell within one of the zip code areas of interest. I also used QGis to convert my clipped CSV files into shapefiles, which I was able to import into Tableau. With Tableau, I was able to perform more visual analysis, especially with regards to numerical calculations, though initially I had trouble joining the shape files since the ACS shapefile had zip codes formatted as Unicode strings, while the point location shapefiles QGis created set the zip code column to integer by default. Tableau wouldn't join the columns because they were different data types. Using QGis and Tableau also helped me see where my data sets needed cleaning.

### Step 3: Cleaning Data
In QGis and Tableau, I originally joined the store data to the zip code shapefile by the zip code of the store's mailing address. In at least one case, the point location's coordinates fell outside of or adjacent to the boundaries of its' mailing address zip code. In some cases, like a Starbucks in St. Paul with a Minneapolis zip code, this was due to a data error. In other cases, typically those on the edge of a zip code area, it is likely due to the difference between the Census defined ZCTA and the zip codes as assigned by the USPS. I originally wanted to use the zip codes as defined by the stores themselves, but due to the number of discrepancies between store mailing zip codes and the ZCTAs in which stores fell, I decided to analyze stores by the ZCTA in which they were located. This required QGis to join the point shapefile to the ZCTA shapefile.

Finally, I had to make sure my zip code data was properly formatted in QGis before attempting to use it in Tableau. By default, QGis converted my zip code data from Unicode to integer. I had to use the "Refactor fields" geoprocessing tool to make sure my zip codes were considered strings before saving my shapefiles.

### Step 4: Exploratory Analysis - Second Round
With clean, formatted data I was able to return to Tableau and join my three data sets - the Census data, the Caribou Coffee data, and the Starbucks data. I've begun making some nice visualizations in Tableau, which can be found here:

https://public.tableau.com/profile/jennifer5948#!/vizhome/coffeecities/TotalPerZip

This is a workbook in progress, but I've begun making some visualizations. Of note:
1. There are 210 Caribou Coffee shops in the area of interest, and only 171 Starbucks Coffee shops.
2. Downtown Minneapolis (55402) has the most coffee shops total (14), with suburban Woodbury (55125) right behind it (12).
3. The Caribou-only zip codes with the most stores are 55303 in Oak Grove and 55101 in downtown St. Paul, with 4 Caribou and 0 Starbucks.
4. The Starbucks-only zip code with the most stores is 55104 in St. Paul, with 3 Starbucks and 0 Caribou.
