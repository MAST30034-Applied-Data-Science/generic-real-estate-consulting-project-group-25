from geopy.geocoders import Nominatim
import requests
import re

#Converting address/name of location strings to long and lat
def addressToCords(address: str):    
    geolocator = Nominatim(user_agent="addToCords")
    location = geolocator.geocode(address)
    if location is None:
        try:
            # Getting rid of unit number
            address = re.sub("^.+\/", "", address)
            location = geolocator.geocode(address)
            return [location.latitude, location.longitude]
        except:
            # Only using one block as a reference 
            try:
                address = re.sub("[0-9]+\-", "", address)
                location = geolocator.geocode(address)
                return [location.latitude, location.longitude]
            except AttributeError:
                return "Requires Manual Inspection"        

    return [location.latitude, location.longitude]
 


#Find driving distance between two places 
# This code requires an OpenRouteService backend running on localhost
# Refer to: https://giscience.github.io/openrouteservice/
def dist_between_two_lat_lon(lat1, lat2, long1, long2, method = "driving-car"):
    response = requests.get(f"http://localhost:8080/ors/v2/directions/{method}?&start={long1},{lat1}&end={long2},{lat2}")
    return response.json()["features"][0]["properties"]["segments"][0]["distance"]

#Get the closest location to a given house in rent dataset. 
#Provided that external data and rent data already have geocord as column
def find_closest_location(rent_cord, ext, ext_cord_col):
    ext_cord = ext[ext_cord_col]    
    return min(ext_cord, key=lambda x: dist_between_two_lat_lon(rent_cord[0], x[0], rent_cord[1], x[1]))


def assign_closest_location(rent, ext, ext_name, rent_cor_col, ext_cor_col):
    import numpy as np
    func = lambda x: find_closest_location(x, ext, rent_cor_col, ext_cor_col)
    rent_geo = rent[[rent_cor_col]].to_numpy()
    vfunc = np.vectorize(func)
    rent_geo = vfunc(rent_geo)
    rent[f'closest_{ext_name}'] = rent_geo.tolist()
    return rent
    




