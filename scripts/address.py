from ast import Index
from time import time
from geopy.geocoders import Nominatim
import requests
import re
from geopy.exc import GeocoderUnavailable
import json

#Converting address/name of location strings to long and lat
def addressToCords(address: str):  
    # Getting rid of unit number and only using one block as reference to help with search
    address = re.sub("^.+\/", "", address)
    address = re.sub("[0-9]+\-", "", address) 
    geolocator = Nominatim(user_agent="addToCords")
    
    try:
        location = geolocator.geocode(address, timeout=5)
        return location.latitude, location.longitude
    except GeocoderUnavailable:
        try:
            query = re.sub(" ", "+", address)
            query = re.sub(",", "%2C", query)
            url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"   
            location = requests.get(url).json()
            return location[0]["lat"], location[0]["lon"]  
        except IndexError:
            return "Requires Manual Inspection"
    except AttributeError:   
        return "Requires Manual Inspection"

def find_min_dist(lat, lng, ext_data, ext_lat_col, ext_lng_col, ext_name_col, method = "driving-car"):
    MAX_ROUTE = 100
    distances = []
    sources = [[lng, lat]]
    for n in range(1, int(len(ext_data)/MAX_ROUTE)+1):
        end = n*MAX_ROUTE
        if n*MAX_ROUTE > len(ext_data):
            end = len(ext_data)
        for i in range(0, end):
            lng_ext = ext_data[ext_lng_col][i] 
            lat_ext = ext_data[ext_lat_col][i]
            sources.append([lng_ext, lat_ext])        
        data = {
                    "locations":sources,
                    "destinations":[0],
                    "metrics":["distance"],
                    "sources":[x for x in range(1, len(sources))]
                }
        response = requests.post(f"http://localhost:8080/ors/v2/matrix/{method}", json = data)
        result = response.json()["distances"]
        distances += result
    
    dst = min(result)
    loc = ext_data[ext_name_col][result.index(dst)]

    return dst, loc


#Get the closest location to a given house in rent dataset. 
#Provided that external data and rent data already have geocord as column
def find_closest_location(rent_lat, rent_long, ext_data, ext_lat_col, ext_lon_col, name_col):
    ext_data["cords"] = ext_data[[ext_lat_col, ext_lon_col, name_col]].values.tolist()
    closest = min(ext_data["cords"], key=lambda x: dist_between_two_lat_lon(rent_lat, x[0], rent_long, x[1]))
    return dist_between_two_lat_lon(rent_lat, closest[0], rent_long, closest[1]), closest[2]



#Find driving distance between two places 
# This code requires an OpenRouteService backend running on localhost
# Refer to: https://giscience.github.io/openrouteservice/
def dist_between_two_lat_lon(lat1, lat2, long1, long2, method = "driving-car"):
    response = requests.get(f"http://localhost:8080/ors/v2/directions/{method}?&start={long1},{lat1}&end={long2},{lat2}")
    try:
        return response.json()["features"][0]["properties"]["segments"][0]["distance"]
    except KeyError:
        return 100000
def assign_closest_location(rent, ext, ext_name, rent_cor_col, ext_cor_col):
    import numpy as np
    func = lambda x: find_closest_location(x, ext, rent_cor_col, ext_cor_col)
    rent_geo = rent[[rent_cor_col]].to_numpy()
    vfunc = np.vectorize(func)
    rent_geo = vfunc(rent_geo)
    rent[f'closest_{ext_name}'] = rent_geo.tolist()
    return rent
    




