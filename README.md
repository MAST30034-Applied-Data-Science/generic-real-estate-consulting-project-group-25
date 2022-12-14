# Generic Real Estate Consulting Project
All commands are assumed to be run from the root folder if not specified otherwise. Some plots have difficulties rendering when viewed from the web version of GitHub. Therefore, it is recommended to use Visual Studio Code, as plots render as required.

## External Datasets Used:
(DataVic)
1. [Vicotria Suburb Data](https://data.gov.au/data/dataset/af33dd8c-0534-4e18-9245-fc64440f742e/resource/4494abe0-64ea-4fa6-931a-d1a389a14e57/download/vic_localities.zip)
2. [Victoria Local Government Area (Local Cities/Councils) Data](https://datashare.maps.vic.gov.au/search?md=bc822a9c-3766-57ac-a034-bcad3fb66d86)
3. Victoria Train Stations Data: [Metro](https://discover.data.vic.gov.au/dataset/ptv-metro-train-stations), [Vline](https://discover.data.vic.gov.au/dataset/ptv-regional-train-stations)

Note: For 2 and 3
 * Projection: Geographicals on GDA2020
 * Buffer: no buffer
 * Format: ESRi shape file


## External APIs Used:
1. Open Route Service: A Local backend was setup to avoid call limitations of the API. Follow [here](https://giscience.github.io/openrouteservice/installation/Installation-and-Usage.html) for a detailed description of how to set up and use the backend service. [OSM Data](http://download.geofabrik.de/australia-oceania/australia.html) and [GitHub Repo](https://github.com/GIScience/openrouteservice) are required for set-up. 

2. Overpass API, Nominatim API (Public, doesn't require API key)

## Overview of Notebooks
1. Scraping, scraping_old_listing, getparks - Scrapes listing and external datasets.

2. Preprocessing, addressConv, routeCalc, count, crime - Cleaning and Feature Engineering of listing and external datasets.

3. Analysis, Distance Analysis, Ext_Analysis - analysis of internal and external feature datasets.

4. Prediction  - Forecasting model for median rental price.

5. **Summary** - Overview of the entire project.

## Required data
0. Please create an environment with Python 3.8 or Python 3.10 installed and install the needed libraries from requirements.txt.
1. Please download the `useragents.txt` (provided under MIT License) in the following way:
    ```shell
    cd data
    wget https://raw.githubusercontent.com/DavidWittman/requests-random-user-agent/master/requests_random_user_agent/useragents.txt
    cd ..
    ```
2. Run the notebook `Scrape.ipynb` or directly from the command line `cd scripts/ && python scrape.py` to get the scraped properties.
3. Visualisation requires shapefiles from the Australian government:
    ````shell
    mkdir -p './data/raw/Suburb Shapes' && cd './data/raw/Suburb Shapes'
    wget https://data.gov.au/data/dataset/af33dd8c-0534-4e18-9245-fc64440f742e/resource/4494abe0-64ea-4fa6-931a-d1a389a14e57/download/vic_localities.zip -O temp.zip
    unzip -o temp.zip
    rm temp.zip
    pwd
    cd ../../..
    ```
4. Some data was obtained and joined via hand.

## Note to tutors:
* Data produced in the process can be found in [Google Drive](https://drive.google.com/drive/folders/1ZJN1-Qbp9L9iqwoMtGhii0ioXq_E_-_0?usp=sharing):

