from ast import Index
from time import time
from geopy.geocoders import Nominatim
import requests
import re
from geopy.exc import GeocoderUnavailable

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

 


#Find driving distance between two places 
# This code requires an OpenRouteService backend running on localhost
# Refer to: https://giscience.github.io/openrouteservice/
def dist_between_two_lat_lon(lat1, lat2, long1, long2, method = "driving-car"):
    response = requests.get(f"http://localhost:8080/ors/v2/directions/{method}?&start={long1},{lat1}&end={long2},{lat2}")
    try:
        return response.json()["features"][0]["properties"]["segments"][0]["distance"]
    except KeyError:
        return 100000


#Get the closest location to a given house in rent dataset. 
#Provided that external data and rent data already have geocord as column
def find_closest_location(rent_lat, rent_long, ext_data):
    ext_data["cords"] = ext_data[["Latitude", "Longitude"]].values.tolist()
    closest = min(ext_data["cords"], key=lambda x: dist_between_two_lat_lon(rent_lat, x[0], rent_long, x[1]))
    return dist_between_two_lat_lon(rent_lat, closest[0], rent_long, closest[1]), closest


def assign_closest_location(rent, ext, ext_name, rent_cor_col, ext_cor_col):
    import numpy as np
    func = lambda x: find_closest_location(x, ext, rent_cor_col, ext_cor_col)
    rent_geo = rent[[rent_cor_col]].to_numpy()
    vfunc = np.vectorize(func)
    rent_geo = vfunc(rent_geo)
    rent[f'closest_{ext_name}'] = rent_geo.tolist()
    return rent
    




