import requests
import time
session = requests.Session()
import pandas as pd
from bs4 import BeautifulSoup
import lxml
import xml.etree.ElementTree as ET
from tqdm import tqdm

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
            "accept": "application/json"}

SITEMAP = "https://www.domain.com.au/sitemap-listings-rent.xml"


def _get_website(seed, json, text):
    response = session.get(seed, headers=HEADERS)
    if json:
        data = response.json()
    elif text:
        data = response.text
    return data


def get_write_listing_groups(w_loc="../data/raw/listing_groups.csv"):
    listings_groups = []
    try:
        data = _get_website(SITEMAP, False, True)
        soup = BeautifulSoup(data, "html.parser")
        listings_groups = [x.contents[0] for x in soup.find_all('loc')]
        listings_groups = pd.DataFrame(listings_groups, columns=['links'])
        listings_groups.to_csv(w_loc)
    except Exception as e:
        print(e)

    return listings_groups


def get_listings_data(loc = "../data/raw/listing_groups.csv"):
    listings_groups = pd.read_csv(loc)
    listings = []
    try:
        for group in listings_groups['links']:
            data = _get_website(group, False, True)
            soup = BeautifulSoup(data, "html.parser")
            listings.extend([x.contents[0] for x in soup.find_all('loc') if '-vic-' in x.contents[0]])
    except Exception as e:
        print(e)

    return listings


def get_datasets(write=False):
    _ = get_write_listing_groups()
    listings = pd.DataFrame(get_listings_data(), columns=['links'])


    prop_list = []
    sub_list = []
    neigh_list = []
    school_list = []
    for i in tqdm(range(0, len(listings))):
        try:
            # response = session.get(listings['links'][i], headers=HEADERS)
            # listing_data = response.json()
            listing_data =_get_website(listings['links'][i], True, False)
            
            if ('redirect' in listing_data.keys()):
                print("Redirected: ", i, listings['links'][i])
                # response = session.get("https://www.domain.com.au/" + listing_data['redirect']['destination'], headers=HEADERS)
                # listing_data = response.json()

                listing_data = _get_website("https://www.domain.com.au/" + listing_data['redirect']['destination'], True, False)
            elif ('props' not in listing_data.keys()):
                print("No props at index: ", i, listings['links'][i])
                
            

            # create property dataset
            prop_data = listing_data['props']['listingSummary']
            # prop_data.pop("stats", None)
            prop_data.pop("showDefaultFeatures", None)
            prop_data.pop("tag", None)

            stats = listing_data['props']['listingSummary']['stats']
            for d in stats:
                stat = {}
                stat[d['key']] = d['value']
                prop_data.update(stat)

            prop_data['id'] = listing_data['props']['id']
            prop_list.append(prop_data)


            # create suburb dataset
            # edit this to add or remove suburb features
            suburb_keys = ["suburb", "medianRentPrice"]


            suburb_data = {key: listing_data['props']['suburbInsights'][key] for key in suburb_keys}
            suburb_data.update(listing_data['props']['suburbInsights']["demographics"])
            suburb_data.pop("clarification", None)
            suburb_data['id'] = listing_data['props']['id']
            sub_list.append(suburb_data)


            # create neighbourhood dataset
            neighbourhood_data = listing_data['props']['neighbourhoodInsights']
            neighbourhood_data.pop('map', None)
            neighbourhood_data.pop('showIncomeAndExpenses', None)
            neighbourhood_data['id'] = listing_data['props']['id']
            neigh_list.append(neighbourhood_data)


            # create closest school dataset
            closest_schools = listing_data['props']['schoolCatchment']['schools']
            top = closest_schools[0]
            top['id'] = listing_data['props']['id']
            top.pop("domainSeoUrlSlug", None)
            top.pop("isRadiusResult", None)
            school_list.append(top)
            time.sleep(0.3)
        except Exception as e:
            print(e)
            
        
    prop_list = pd.DataFrame(prop_list)
    sub_list = pd.DataFrame(sub_list)
    neigh_list = pd.DataFrame(neigh_list)
    school_list = pd.DataFrame(school_list)
    if write:
        prop_list.to_csv('../data/raw/listing_properties.csv')
        sub_list.to_csv('../data/raw/suburb_stat.csv')
        neigh_list.to_csv('../data/raw/neigh_stat.csv')
        school_list.to_csv('../data/raw/closest_school.csv')
    return prop_list, sub_list, neigh_list, school_list


prop_list, sub_list, neigh_list, school_list = get_datasets()
print(prop_list)