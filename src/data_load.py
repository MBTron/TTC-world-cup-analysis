# functions to load GTFS into dataframes
import pandas as pd
from .config import get_data_directories

def load_gtfs_tables(): 
    """
    Loads all main GTFS files into Pandas DataFrames. 
    Returns: stops, routes, trips, stop_times, calendar, shapes
    """
    dirs = get_data_directories()
    gtfs_dir = dirs['gtfs']

    required_files = ['stops.txt', 'routes.txt', 'trips.txt', 'stop_times.txt', 'calendar.txt', 'shapes.txt']

    for file in required_files:
        if not (gtfs_dir / file).exists():
            raise FileNotFoundError(f"Required GTFS file not found: {file}")
            print(f"Required GTFS file not found: {file}")

    try: 
        stops = pd.read_csv(gtfs_dir / "stops.txt", low_memory=False)
        # print(f"Read in stops")
        routes = pd.read_csv(gtfs_dir / "routes.txt", low_memory=False)
        # print(f"Read in routes")
        trips = pd.read_csv(gtfs_dir / "trips.txt", low_memory=False)
        # print(f"Read in trips")
        stop_times = pd.read_csv(gtfs_dir / "stop_times.txt", low_memory=False)
        # print(f"Read in stop_times")
        calendar = pd.read_csv(gtfs_dir / "calendar.txt", low_memory=False)
        # print(f"Read in calendar")
        shapes = pd.read_csv(gtfs_dir / "shapes.txt", low_memory=False)
        # print(f"Read in shapes")
            
    except pd.errors.ParserError as e: 
        raise ValueError(f"Error parsinng GTFS file: {e}")
        print(f"Error parsinng GTFS file: {e}")
        
    return stops, routes, trips, stop_times, calendar, shapes