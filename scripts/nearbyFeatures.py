import requests

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

def getAll(type:str, amenity:str, box = "-39.192401, 141.028939, -34.005138, 151.077642"):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (node["{type}"="{amenity}"]({box});
    );
    out;
    """
    response = requests.get(overpass_url, 
                            params={'data': overpass_query})
    data = response.json()

    return data