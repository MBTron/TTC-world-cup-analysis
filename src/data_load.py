# functions to load GTFS into dataframes
import pandas as pd
from src.config import GTFS_DIR

def load_gtfs_tables(): 
    """
    Loads all main GTFS files into Pandas DataFrames. 
    Returns: stops, routes, trips, stop_times, calendar
    """
    stops = pd.read_csv(GTFS_DIR / "stops.txt")
    routes = pd.read_csv(GTFS_DIR / "routes.txt")
    trips = pd.read_csv(GTFS_DIR / "trips.txt")
    stop_times = pd.read_csv(GTFS_DIR / "stop_times.txt")
    calendar = pd.read_csv(GTFS_DIR / "calendar.txt")
    
    return stops, routes, trips, stop_times, calendar