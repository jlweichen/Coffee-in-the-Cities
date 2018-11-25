# Coffee in the Cities: Analysis of the Battleground between Caribou Coffee and Starbucks

## Introduction
Though I personally don't drink much coffee, it isn't hard to find someone who does. Coffee shops are a daily routine for some, and an occasional treat for others. They cater to students, professionals, travelers, and more with comfortable seating and warm ambiance. There are plenty of options for those who want a sip prepared for them on their way to work, school, or errands. In the Twin Cities, two players have a formidable presence: Caribou Coffee and Starbucks Coffee.

### Caribou Coffee
This chain started in the 1990s, and is especially known in the Midwest. Caribou Coffee has a huge presence in the Twin Cities, which is not a surprise considering that their first coffee shop opened in Edina. By the way, it's still there on 44th and France.
If you need further proof of the chain's proliferation in the area, there are five stores at the Mall of America! <a href= "https://locations.cariboucoffee.com/us">However, good luck finding them elsewhere</a>. There are a smattering of locations on the East Coast, mainly in popular Southern cities, but Caribou Coffee is unknown in the Mid-Atlantic and New England states. There currently aren't any international stores.

### Starbucks Coffee
Known worldwide, this is the home of Pike Place roast and Pumpkin Spice Lattes. There's plenty of Starbucks locations worldwide, and the Twin Cities has its' fair share.
Starbucks coffee shops are attached to many Target stores, and with Target being headquartered in the area, there are many Target stores here; thus, many Twin Cities Starbucks are actually licensed locations inside Target stores. This is in addition to other fond Starbucks licensees such as grocery stores, colleges, and airports. For the sake of this analysis I will not differentiate between corporate and licensed stores, but in a future Starbucks-specific analysis, I may.

## Data
I used three main sources of data for this analysis. For the <a href = 'https://locations.cariboucoffee.com/'>Caribou Coffee</a> and <a href ='https://www.starbucks.com/store-locator'>Starbucks Coffee</a> locations, I used their respective websites. For shapefile and Census data, I used data provided by the <a href='https://metrocouncil.org/Data-and-Maps.aspx'>Metropolitan Council</a> and made available for download through the <a href='https://gisdata.mn.gov'>Minnesota Geospatial Commons</a>. Specifically, I used the <a href = 'https://gisdata.mn.gov/dataset/us-mn-state-metc-society-census2000tiger-zcta'>Census 2000 5-Digit ZIP Code Tabulation Areas (ZCTAs)</a> shapefile for zip code boundaries, and <a href = 'https://gisdata.mn.gov/dataset/us-mn-state-metc-society-census-acs'>American Community Survey 5-Year Summary File</a>, containing the 2012-2016 five-year ACS estimates, for more insight on each zip code's population and demographics.

## Methodology

### Step 1: Scraping
The store data was scraped from each store's Store Locator page. I used Python scripts which parsed the store locator results for each zip code in the metro via BeautifulSoup, and aggregated them into a Pandas dataframe. These scrapers can be found at https://github.com/jlweichen/Coffee-in-the-Cities/tree/master/scrapers. I created two CSV files with point location data - one for Caribou and one for Starbucks. I also collected zip code information for each store.

### Step 2: Exploratory Analysis
I exported the CSV files into QGis and Tableau for exploratory analysis. I joined this data with the ACS and shapefile data to get a cursory glance. Some stores fell on the outer periphery of the search area, and I used QGis's "Clip" function to curtail my analysis only to those stores that fell within one of the zip code areas of interest. I also used QGis to convert my clipped CSV files into shapefiles, which I was able to import into Tableau. With Tableau, I was able to perform more visual analysis, especially with regards to numerical calculations. Using QGis and Tableau also helped me see where my data sets needed cleaning.

### Step 3: Cleaning Data
In QGis and Tableau, I joined the store data to the zip code shapefile by the zip code of the store's mailing address. In at least one case, the point location's coordinates fell outside of or adjacent to the boundaries of its' mailing address zip code. The only locations with mailing address zip codes not represented by a shapefile are the Starbucks and Caribou stores in Terminal 1 of the Minneapolis-Saint Paul International Airport, which has the USPS zip code 55111. Because this zip code is a subset within the boundaries of zip code 55450, I used this zip code to substitute for 55111 for analysis and edited my scraper code to reflect this.
