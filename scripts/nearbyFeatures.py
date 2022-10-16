import requests

def getAllFeatures(key:str, value:str, box = "-39.192401, 141.028939, -34.005138, 151.077642"):
    """
    Gets all features of a specific key category within a rentangular bounding box.
    (The default bounding box includes whole of Victoria and partial NSW)
    
    key, value: plug in values based on: https://wiki.openstreetmap.org/wiki/Key:amenity
    return: List of corresponding features in json file format
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (node[{key}={value}]({box});
    );
    out;
    """
    response = requests.get(overpass_url, 
                            params={'data': overpass_query})
    data = response.json()
    return data