#Converitng address/name of location strings to long and lat
def addressToCords(address: str):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="addToCords")
    location = geolocator.geocode(address)
    return [location.latitude, location.longitude]

#Find distance between two places with geocords    
def dist_between_two_lat_lon(*args):
    from math import asin, cos, radians, sin, sqrt
    lat1, lat2, long1, long2 = map(radians, args)

    dist_lats = abs(lat2 - lat1) 
    dist_longs = abs(long2 - long1) 
    a = sin(dist_lats/2)**2 + cos(lat1) * cos(lat2) * sin(dist_longs/2)**2
    c = asin(sqrt(a)) * 2
    radius_earth = 6378 # the "Earth radius" R varies from 6356.752 km at the poles to 6378.137 km at the equator.
    return c * radius_earth

#Get the closest location to a given house in rent dataset. 
#Provided that external data and rent data already have geocord as column
def find_closest_location(rent_row, ext):
    rent_cord = rent_row["geocord"]
    ext_cord = ext["geocord"]
    return min(ext_cord, key=lambda x: dist_between_two_lat_lon(rent_cord[0], x[0], rent_cord[1], ext[1]))


def assign_closest_location(rent, ext, ext_name):
    import numpy as np
    func = lambda x: find_closest_location(x, ext)
    rent_geo = rent["geoloc"].to_numpy()
    vfunc = np.vectorize(func)
    rent_geo = vfunc(rent_geo)
    rent[f'closest_{ext_name}'] = rent_geo.tolist()
    return rent
    




