import requests
from address import dist_between_two_lat_lon

def nearbyFeatures(lat, lng, radius, type: str, amenity:str):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (node(around:{radius},{lat},{lng})
    ["{type}"="{amenity}"];
    );
    out;
    """
    response = requests.get(overpass_url, 
                            params={'data': overpass_query})
    data = response.json()

    return data

def getAllStation(box = "-39.192401, 141.028939, -34.005138, 151.077642"):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (node["railway"="station"]({box});
    node["railway"="stop"]({box});
    );
    out;
    """
    response = requests.get(overpass_url, 
                            params={'data': overpass_query})
    data = response.json()

    return data

def getNearestStation(lat_lst, lng_lst, lat, lng, radius = 1000):
    inc = 1000
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (node(around:{radius},{lat},{lng})["railway"="station"];
    (node(around:{radius},{lat},{lng})["railway"="stop"]
    );
    out;
    """
    response = requests.get(overpass_url, 
                            params={'data': overpass_query})
    data = response.json()
    if data["elements"] == []:
        return getAllStation(lat, lng, radius+inc)
    else:
        n = len(data["elements"])
        dst = []
        for i in range(0, n):
            lat_st = data["elements"][i]["lat"]
            lng_st = data["elements"][i]["lon"]
            dst.append(dist_between_two_lat_lon(lat_st, lat_lst, lng_st, lng_lst))
        return min(dst)
