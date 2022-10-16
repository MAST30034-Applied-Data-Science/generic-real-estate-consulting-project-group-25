# Generic Real Estate Consulting Project
All commands are assumed to be run from the root folder if not specified otherwise.

## External Datasets Used:
(DataVic)
1. [Victoria Locality (Suburb) Data](https://data.gov.au/dataset/ds-dga-af33dd8c-0534-4e18-9245-fc64440f742e/details) 
2. [Victoria Local Government Area (Local Cities/Councils) Data](https://datashare.maps.vic.gov.au/search?md=bc822a9c-3766-57ac-a034-bcad3fb66d86)
3. Victoria Train Stations Data: [Metro](https://discover.data.vic.gov.au/dataset/ptv-metro-train-stations), [Vline](https://discover.data.vic.gov.au/dataset/ptv-regional-train-stations)

Note: 2 and 3 require order through email, ESRI shapefile format was used for all regions of Victoria.

## External APIs Used:
1. Open Route Service: A Local backend was setup to avoid call limitations of the API. Follow [here](https://giscience.github.io/openrouteservice/installation/Installation-and-Usage.html) for a detailed description on how to set up and use the backend service. [OSM Data](http://download.geofabrik.de/australia-oceania/australia.html) and [GitHub Repo](https://github.com/GIScience/openrouteservice) are required for set-up. 

2. Overpass API, Nominatim API (Public, doesn't require API key)

## Overview of Notebooks
1. Scraping, scraping_old_listing, getparks - Scrapes listing and external datasets.

2. Preprocessing, addressConv, routeCalc - Cleaning and Feature Engineering of listing and external datasets.

3. Analysis, Distance Analysis, Ext_Analysis - analysis of internal and external feature datasets.

4. Prediction  - Forecasting model for median rental price.

5. **Summary** - Overview of entire project.

## Scraping
1. Please download the `useragents.txt` (provided under MIT License) in the following way:
    ```shell
    cd data
    wget https://raw.githubusercontent.com/DavidWittman/requests-random-user-agent/master/requests_random_user_agent/useragents.txt
    cd ..
    ```
2. Run the notebook `Scrape.ipynb` or directly from the command line `cd scripts/ && python scrape.py`{:.language-shell}