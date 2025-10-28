import pandas as pd
import folium

def plot_route_map(
    trips: pd.DataFrame,
    stop_times: pd.DataFrame,
    stops: pd.DataFrame,
    headway_stats: pd.DataFrame
) -> folium.Map:
    """
    Plots the stops used by the trips for a given route on a Folium map.
    
    Args:
        trips (pd.DataFrame): The filtered trips DataFrame (e.g., for one route).
        stop_times (pd.DataFrame): The full stop_times DataFrame.
        stops (pd.DataFrame): The full stops DataFrame containing coordinates.
        headway_stats (pd.DataFrame): DataFrame with headway statistics for each stop.
        
    Returns:
        folium.Map: A Folium map object.
    """
    
    # 1. Select the stop_times relevant to the filtered route_trips (using trip_id)
    # This links the route's trips to the stops they service.
    route_stop_times = stop_times.merge(
        trips[['trip_id']], 
        on='trip_id', 
        how='inner'
    )
    
    # 2. Get unique stop IDs used by this route
    unique_stop_ids = route_stop_times['stop_id'].unique().tolist()
    
    # 3. Filter the stops DataFrame to just the stops used by the route
    route_stops = stops[stops['stop_id'].isin(unique_stop_ids)].copy()
    
    # Check if we have any stops to plot
    if route_stops.empty:
        # Create a default map centered on Toronto (approx.)
        m = folium.Map(location=[43.6532, -79.3832], zoom_start=12, tiles='CartoDB Positron')
        return m

    # 4. Initialize Folium Map centered on the average stop location
    avg_lat = route_stops['stop_lat'].mean()
    avg_lon = route_stops['stop_lon'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13, tiles='CartoDB Positron')
    
    # Marker for the World Cup venue (BMO Field / Exhibition Place)
    BMO_LAT, BMO_LON = 43.6331, -79.4184 # Coordinates for BMO Field
    folium.Marker(
        [BMO_LAT, BMO_LON], 
        popup='BMO Field - World Cup 2026 Venue',
        icon=folium.Icon(color='red', icon='star') # Use a star icon to denote importance
    ).add_to(m)

    # 5. Add markers for each stop
    for index, row in route_stops.iterrows():
        # Ensure row contains stop_lat and stop_lon
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=5,
            color='#3498db',
            fill=True,
            fill_color='#3498db',
            fill_opacity=0.7,
            tooltip=row['stop_name'] # Show stop name on hover
        ).add_to(m)
        
    return m
