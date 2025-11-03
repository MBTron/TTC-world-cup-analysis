from math import radians, cos, sin, asin, sqrt
import pandas as pd

def haversine_distance(lat1, lon1, lat2, lon2): 
    """ 
    Calculate greater circle distance between two points on Earth. 
    Returns distance in meters.
    """
    # convert to rads 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine forumula 
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    # earth radius (m)
    r = 6371000
    
    return c * r

def find_stops_near_location(stops, lat, lon, max_distance_m=1000):
    """
    Find all stops within max_distance_m of a location.

    Args: 
        stops: dataframe with stop_lat, stop_lon columns
        lat, lon: Target location coordinates
        max_distance_m: Maximum distance in meters
    """
    stops = stops.copy()

    # calculate the distance for each stop
    stops['distance_m'] = stops.apply(
        lambda row: haversine_distance(
            row['stop_lat'], row['stop_lon'], lat, lon   
        ), 
        axis = 1
    )

    # filter to nearby stops 
    nearby = stops[stops['distance_m'] <= max_distance_m].copy()
    
    # Sort by distance
    nearby = nearby.sort_values('distance_m')
    
    # Add walking time estimate (80m/min = typical walking speed)
    nearby['walk_time_min'] = (nearby['distance_m'] / 80).round(1)

    return nearby