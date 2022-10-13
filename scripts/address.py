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

def find_min_dist(lat, lng, ext_data, ext_lat_col, ext_lng_col, ext_name_col, method = "driving-car"):
    """
    Find the closest driving distance between a starting coordinate and a list of destination coordinates
    This code requires an local OpenRouteService core service running simultaneously 
    Refer to: https://giscience.github.io/openrouteservice/ fpor instructions on installation and usuage

    lat: latitude of starting coordinate
    lng: longitude of starting coordinate 
    ext_data: a pandas dataframe containing the destinations and their geocordinates
    ext_lat_col: column name of ext_data that stores latitude
    ext_lng_col: column name of ext_data that stores longitude 
    ext_name_col: column name of ext_data that stores the name of the destination
    """ 

    sources = [[lng, lat]]
    # Getting the distance into the required format
    for i in range(0, len(ext_data)):
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
    
    dst = min(result)
    loc = ext_data[ext_name_col][result.index(dst)]

    return dst, loc







        
    




