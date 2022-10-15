import requests
import time

import pandas as pd
from bs4 import BeautifulSoup
import lxml
import xml.etree.ElementTree as ET
from tqdm import tqdm
import random
import re
import os

session = requests.Session()


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
    "accept": "application/json"}

SITEMAP = "https://www.domain.com.au/sitemap-listings-rent.xml"

"""Function to get data from json response."""
def _get_website(seed: str, json: bool, text: bool):
    """
    Function to get the content of a website

    :param seed: url to scrape
    :param json: True if response is wanted in the json format
    :param text: True if response is wanted in the plaintext format
    :return: content of website, as a dictionary or string
    """
    response = session.get(seed, headers=HEADERS)
    if json:
        data = response.json()
    elif text:
        data = response.text
    return data

"""Function to get all listing endpoints"""
def get_write_listing_groups(w_loc: str = "../data/raw/listing_groups.csv"):
    """
    Function to get every link from the sitemap of domain.com.au

    :param w_loc: path where to save the scraped urls.
    :return: dataframe of scraped listings
    """
    listings_groups = []
    try:
        data = _get_website(SITEMAP, False, True)
        soup = BeautifulSoup(data, features="xml")
        listings_groups = [x.contents[0] for x in soup.find_all('loc')]
        listings_groups = pd.DataFrame(listings_groups, columns=['links'])
        listings_groups.to_csv(w_loc)
    except Exception as e:
        print(e)

    return listings_groups

"""Function returns all enpoints of listings of interest """
def get_listings_data(loc: str = "../data/raw/listing_groups.csv") -> pd.DataFrame:
    """
    Function to scrape all urls that are to related to rental properties in Victoria.

    :param loc: path where to save the different property urls.
    :return: dataframe containg all urls of properties in Victoria.
    """
    listings_groups = pd.read_csv(loc)
    listings = []
    try:
        for group in listings_groups['links']:
            data = _get_website(group, False, True)
            soup = BeautifulSoup(data, features="xml")
            listings.extend([x.contents[0] for x in soup.find_all(
                'loc') if '-vic-' in x.contents[0]])
    except Exception as e:
        print(e)

    return listings

"""Function to get dataset from provided endpoints."""
def get_datasets(write: bool = False) -> 'list[pd.DataFrame]':
    """
    Scrapes the website domain.com.au to obtain all the lists of
        - properties
        - suburbs
        - information about the neighbourhood
        - information about schools next to each property
    It performs requests to a public api, and requesting the results in the json format.

    :param write: boolean wether or not save the scraped dataframes as .csv to ../data/raw/
    :return: list of scraped properties in dataframes
    """
    _ = get_write_listing_groups()
    listings = pd.DataFrame(get_listings_data(), columns=['links'])

    prop_list = []
    sub_list = []
    neigh_list = []
    school_list = []
    for i in tqdm(range(0, len(listings))):
        try:

            listing_data = _get_website(listings['links'][i], True, False)

            if ('redirect' in listing_data.keys()):
                print("Redirected: ", i, listings['links'][i])

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
            suburb_keys = ["suburb", "medianRentPrice"]

            suburb_data = {
                key: listing_data['props']['suburbInsights'][key] for key in suburb_keys}
            suburb_data.update(
                listing_data['props']['suburbInsights']["demographics"])
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
            for school in closest_schools:
                school.pop("domainSeoUrlSlug", None)
                school.pop("isRadiusResult", None)
                school['listing_id'] = listing_data['props']['id']
            # top = closest_schools[0]
            # top['id'] = listing_data['props']['id']
            # top.pop("domainSeoUrlSlug", None)
            # top.pop("isRadiusResult", None)
            school_list.extend(closest_schools)
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


# Code to scrape oldlistings.com.au
BASE_URL = 'https://www.oldlistings.com.au'

COLUMNS = ['lat', 'long', 'postal_code', 'address',
           'beds', 'baths', 'cars', 'type', 'price', 'date']
USER_AGENTS = [x.strip() for x in open('../data/useragents.txt', 'r')]

request_counter = 0


class TooManyRequestsError(RuntimeError):
    pass


def get_random_user_agent_header():
    """
    Using the user agent list found at: https://raw.githubusercontent.com/DavidWittman/requests-random-user-agent/master/requests_random_user_agent/useragents.txt,
    chooses random user agents in order to bypass website anti DDoS software.
    :return: a random user agent header.
    """
    return {
        'User-Agent': random.choice(USER_AGENTS)
    }


def get_oldlistings_hrefs():
    """
    Gets the sitemap of oldlistings.com.au and saves it to '../data/raw/to_scrape_oldlistings.txt'.
    """
    SITEMAP_URL = 'https://www.oldlistings.com.au/site-map?{page}state=VIC'
    PATTERN = '\/real-estate\/VIC\/\w*\/\d*\/rent\/'

    for i in range(18):
        print(i)
        if i != 0:
            url = SITEMAP_URL.format(page='page=' + str(i) + '&')
        else:
            url = SITEMAP_URL.format(page='')
        print(url)
        resp = requests.get(url=url, headers=HEADERS)
        urls = re.findall(PATTERN, resp.text)

        with open('../data/raw/to_scrape_oldlistings.txt', 'a+') as f:
            for ref in sorted(list(set(urls))):
                f.write(ref)
                f.write('\n')

        time.sleep(random.randint(2, 5))


def scrape_suburb(suburb: str, postal_code: int) -> pd.DataFrame:
    """
    Wrapper function to generate the url which is needed to scrape

    :param suburb: suburb name to scrape properties from
    :param postal_code: postal code of the suburb
    :return: dataframe containing scraped values of said suburb
    """
    return scrape_from_ref('/real-estate/VIC/' + suburb + '/' + str(postal_code) + '/rent/')


def scrape_from_ref(url: str, max_depth: int = 0) -> pd.DataFrame:
    """
    Scrapes oldlistings.com.au for propertie prices, given the url of the suburb of interest. Each url may have 0 or 
    many subpages, which are then recursively called.

    :param url: suburb of listings the page is going to scrape.
    :param max_depth: used to limit the number of subpages the scraper visits for a given suburb.
    :return: dataframe containing properties of said suburb, with the following fields
        ['lat', 'long', 'postal_code', 'address', 'beds', 'baths', 'cars', 'type', 'price', 'date']
    """
    global request_counter

    # if max_depth == 2:
    #     return pd.DataFrame(columns=COLUMNS)
    # print(BASE_URL+url)

    df = pd.DataFrame(columns=COLUMNS)

    try:
        resp = requests.get(
            url=BASE_URL + url, headers=get_random_user_agent_header())
        soup = BeautifulSoup(resp.text, features="xml")
        elems = soup.select('div.property.clearfix')
        request_counter += 1
        print('req url: ', BASE_URL + url, 'status code:', resp.status_code)
        if resp.status_code == 403:
            raise TooManyRequestsError(
                f"Forbidden after {request_counter} requests")
    except TooManyRequestsError:
        raise  # to stop putting out requests to the server
    except Exception as e:
        print(e)
        return pd.DataFrame(columns=COLUMNS)

    for elem in elems:
        lat = elem['data-lat']
        long = elem['data-lng']
        postal_code = url.split('/')[4]
        address = elem.find("h2", {'class': "address"}).text
        beds = int(float(elem.find('p', {'class': 'property-meta bed'}).text.split(':')[1])) if elem.find('p', {
            'class': 'property-meta bed'}) is not None else -1
        baths = int(float(elem.find('p', {'class': 'property-meta bath'}).text.split(':')[1])) if elem.find('p', {
            'class': 'property-meta bath'}) is not None else -1
        cars = int(float(elem.find('p', {'class': 'property-meta car'}).text.split(':')[1])) if elem.find('p', {
            'class': 'property-meta car'}) is not None else -1
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
        time.sleep(random.randint(5, 15))
        # print(next_url)
        df1 = scrape_from_ref(next_url, max_depth + 1)
        return pd.concat([df, df1], ignore_index=True)

    except IndexError as ie:
        print('done for suburb')
        return df


def scrape_old_listings(start_from: int = 1) -> None:
    """
    Runner function for oldlistings scraper.

    :param start_from: suburb to start from.
    """
    # start_from is the row on which you wish to start scraping from to_scrape_oldlistings.txt

    with open('../data/raw/to_scrape_oldlistings.txt', 'r') as f:
        hrefs = [x.strip() for x in f.readlines()]

    if not os.path.exists('../data/raw/oldlistings/'):
        os.mkdir('../data/raw/oldlistings/')

    for href in tqdm(hrefs[start_from - 1:]):
        # print(href)
        df = scrape_from_ref(href)
        # print(df.shape)
        df.to_csv('../data/raw/oldlistings/' +
                  href.split('/')[3], index=False, mode='w')
        time.sleep(random.randint(10, 15))

if __name__ == "__main__":
    get_datasets(write=True)