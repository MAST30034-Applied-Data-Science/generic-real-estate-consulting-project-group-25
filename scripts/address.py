import requests
import re

def addressToCords(address: str):  
    """
    Converting address/name of location strings to long and lat
    """
    # Getting rid of unit number and only using one block as reference to help with search
    address = re.sub("^.+\/", "", address)
    address = re.sub("[0-9]+\-", "", address) 
    query = re.sub(" ", "+", address)
    query = re.sub(",", "%2C", query)
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"   
    try:
        location = requests.get(url).json()
        return location[0]["lat"], location[0]["lon"] 
    # If there is no matching result, get rid of some non-unique words as sometimes they don't match with the database
    except IndexError:
        try:
            query = re.sub("Drive||Street||Avenue||Road||Court||Crescent", "", query)
            url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"   
            location = requests.get(url).json()
            return location[0]["lat"], location[0]["lon"] 
        # If the address still cannot be found by hand, it needs to be retrieved manually
        except IndexError:
            return "Requires Manual Inspection"
    except AttributeError:   
        return "Requires Manual Inspection"

def find_closest_location(rent_lat, rent_long, ext_data, ext_lat_col, ext_lon_col, name_col):
    """
    Find the closest driving distance between a starting coordinate and a list of destination coordinates
    This code requires an local OpenRouteService core service running simultaneously 
    Refer to: https://giscience.github.io/openrouteservice/ fpor instructions on installation and usuage

    rent_lat: latitude of starting coordinate
    rent_lng: longitude of starting coordinate 
    ext_data: a pandas dataframe containing the destinations and their geocordinates
    ext_lat_col: column name of ext_data that stores latitude
    ext_lng_col: column name of ext_data that stores longitude 
    name_col: column name of ext_data that stores the name of the destination
    """ 
    ext_data["cords"] = ext_data[[ext_lat_col, ext_lon_col, name_col]].values.tolist()
    closest = min(ext_data["cords"], key=lambda x: dist_between_two_lat_lon(rent_lat, x[0], rent_long, x[1]))
    return dist_between_two_lat_lon(rent_lat, closest[0], rent_long, closest[1]), closest[2]


def dist_between_two_lat_lon(lat1, lat2, long1, long2, method = "driving-car"):
    """
    Finding the distance between any two given corrdinates
    """
    response = requests.get(f"http://localhost:8080/ors/v2/directions/{method}?&start={long1},{lat1}&end={long2},{lat2}")
    try:
        return response.json()["features"][0]["properties"]["segments"][0]["distance"]
    # Assign a value if the distance is too far away, and is inappropriate to assume that the residence will use this facility
    except KeyError:
        return 100000




        
    




