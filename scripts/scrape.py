import requests
import time
session = requests.Session()
import pandas as pd
from bs4 import BeautifulSoup
import lxml
import xml.etree.ElementTree as ET
from tqdm import tqdm
import random
import re
import os

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
            prop_data.pop("showDefaultFeatures", None)
            prop_data.pop("tag", None)

            stats = prop_data.pop("stats", None)
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




BASE_URL = 'https://www.oldlistings.com.au'

COLUMNS = ['lat', 'long', 'postal_code', 'address', 'beds', 'baths', 'cars', 'type', 'price', 'date']


def get_oldlistings_hrefs():
    SITEMAP_URL = 'https://www.oldlistings.com.au/site-map?{page}state=VIC'
    PATTERN = '\/real-estate\/VIC\/\w*\/\d*\/rent\/'

    for i in range(18):
        print(i)
        if i != 0:
            url = SITEMAP_URL.format(page='page='+str(i)+'&')
        else:
            url = SITEMAP_URL.format(page='')
        print(url)
        resp = requests.get(url=url, headers=HEADERS)
        urls = re.findall(PATTERN, resp.text)

        with open('../data/raw/to_scrape_oldlistings.txt', 'a+') as f:
            for ref in set(urls):
                f.write(ref)
                f.write('\n')

        time.sleep(random.randint(2, 5))


def scrape_suburb(suburb, postal_code):
    return scrape_from_ref('/real-estate/VIC/'+suburb+'/'+str(postal_code)+'/rent/')


def scrape_from_ref(url, max_depth=0):
    # if max_depth == 2:
    #     return pd.DataFrame(columns=COLUMNS)
    #print(BASE_URL+url)

    df = pd.DataFrame(columns=COLUMNS)

    try:
        resp = requests.get(url=BASE_URL+url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, features="lxml")
        elems = soup.select('div.property.clearfix')
        #print(resp.status_code)
        #print('req url: ', BASE_URL+url)
        #print(resp.text)

    except Exception as e:
        print(e)
        return pd.DataFrame(columns=COLUMNS)

    for elem in elems:
        lat = elem['data-lat']
        long = elem['data-lng']
        postal_code = url.split('/')[4]
        address = elem.find("h2", {'class': "address"}).text
        beds = int(elem.find('p', {'class': 'property-meta bed'}).text.split(':')[1]) if elem.find('p', {'class': 'property-meta bed'}) is not None else -1
        baths = int(elem.find('p', {'class': 'property-meta bath'}).text.split(':')[1]) if elem.find('p', {'class': 'property-meta bath'}) is not None else -1
        cars = int(elem.find('p', {'class': 'property-meta car'}).text.split(':')[1]) if elem.find('p', {'class': 'property-meta car'}) is not None else -1
        # cars is nonexisting zometimes

        category = elem.find('p', {'class': 'property-meta type'}).text.split(':')[
            1].strip() if elem.find('p', {'class': 'property-meta type'}) is not None else -1
        last_price = elem.find('section', {'class': 'price'}).text.split(':')[
            1].strip()
        historical_prices = [x.find_all(text=True) for x in elem.find(
            'section', {'class': 'historical-price'}).find_all('li')]
        for hist_price in historical_prices:
            if len(hist_price) == 2:
                df.loc[len(
                    df)] = lat, long, postal_code, address, beds, baths, cars, category, hist_price[1], hist_price[0]

    try:
        next_url = soup.find_all('li', 'next')[0].a['href']
        time.sleep(random.random())
        #print(next_url)
        df1 = scrape_from_ref(next_url, max_depth+1)
        return pd.concat([df, df1], ignore_index=True)

    except IndexError as ie:
        print('done for suburb')
        return df


def scrape_old_listings():
    with open('../data/raw/to_scrape_oldlistings.txt', 'r') as f:
        hrefs = [x.strip() for x in f.readlines()]

    if not os.path.exists('../data/raw/oldlistings/'):
        os.mkdir('../data/raw/oldlistings/')

    for href in tqdm(hrefs):
        #print(href)
        df = scrape_from_ref(href)
        #print(df.shape)
        df.to_csv('../data/raw/oldlistings/' +
                  href.split('/')[3], index=False, mode='w')
        time.sleep(random.randint(1, 5))


#scrape_old_listings()
