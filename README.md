# Coffee in-the Cities
Analysis of the battleground between Caribou Coffee and Starbucks

## Introduction
Though I personally don't drink much coffee, it's hard to argue that there aren't many others who do. There are plenty of options for those who want a sip prepared for them on their way to work, school, or errands. In the Twin Cities, two players have a formidable presence: Caribou Coffee and Starbucks Coffee.

### Caribou Coffee
This chain started in the 90s, and is especially known in the Midwest. Caribou Coffee has a huge presence in the Twin Cities, which is not a surprise considering that their first coffee shop was opened in Edina. There are five Caribou Coffee locations within the Mall of America! <a href= "https://locations.cariboucoffee.com/us">However, good luck finding them elsewhere</a>. There are a smattering of locations on the East Coast, mainy in Southern states, but as a native of New Jersey, Caribou struck me as a "foreign" chain. However, we have two Dunkin Donuts in every town, which is a uniquely New England and Mid-Atlantic phenomenon.

### Starbucks Coffee
Known worldwide, this is the coffee shop founded in Seattle that made lattes ubiquitous. There's plenty of Starbucks even in the Twin Cities. Starbucks are attached to many Target stores, and with Target being headquartered in the area, many Twin Cities Starbucks are actually licensed locations inside Target stores. For the sake of this analysis I will not differentiate between corporate and licensed stores, but in a future Starbucks-specific analysis, I may.

## Data
I used three main sources of data for this analysis. For the <a href = 'https://locations.cariboucoffee.com/'>Caribou Coffee</a> and <a href ='https://www.starbucks.com/store-locator'>Starbucks Coffee</a> locations, I used their respective websites. For shapefile and Census data, I used data provided by the <a href='https://metrocouncil.org/Data-and-Maps.aspx'>Metropolitan Council</a> and made available for download through the <a href='https://gisdata.mn.gov'>Minnesota Geospatial Commons</a>. Specifically, I used the <a href = 'https://gisdata.mn.gov/dataset/us-mn-state-metc-society-census2000tiger-zcta'>Census 2000 5-Digit ZIP Code Tabulation Areas (ZCTAs)</a> shapefile for zip code boundaries, and <a href = 'https://gisdata.mn.gov/dataset/us-mn-state-metc-society-census-acs'>American Community Survey 5-Year Summary File</a> containing the 2012-2016 five-year ACS estimates.

## Methodology
The store data was scraped from each store's Store Locator page. I used Python scripts which aggregated the store locator results for each zip code in the metro and collected them into a Pandas dataframe. These scrapers can be found at https://github.com/jlweichen/Coffee-in-the-Cities/tree/master/scrapers.
The store data was then joined with the ACS and shapefile data for analysis. I used Geopandas to modify the original zip code shapefiles and join them with the ACS and store data. I joined the store data to the zip code shapefile by the zip code of the store's mailing address. In at least one case, the point location's coordinates fall outside or adjacent to the boundaries of its' mailing address zip code. The only locations with mailing address zip codes not represented by a shapefile are the Starbucks and Caribou stores in Terminal 1 of the Minneapolis-Saint Paul International Airport, which has the USPS zip code 55111. Because this zip code is a subset within the boundaries of zip code 55450, I used this zip code to substitute for 55111 for analysis.
