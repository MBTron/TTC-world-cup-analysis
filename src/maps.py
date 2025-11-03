import pandas as pd
import folium

def plot_route_map(
    trips: pd.DataFrame,
    stop_times: pd.DataFrame,
    stops: pd.DataFrame,
    headway_stats: pd.DataFrame,
    shapes: pd.DataFrame
) -> folium.Map:
    """
    Plots the stops and route lines for a given route on a Folium map.
    
    Args:
        trips (pd.DataFrame): The filtered trips DataFrame (e.g., for one route).
        stop_times (pd.DataFrame): The full stop_times DataFrame.
        stops (pd.DataFrame): The full stops DataFrame containing coordinates.
        headway_stats (pd.DataFrame): DataFrame with headway statistics for each stop.
        shapes (pd.DataFrame): The shapes DataFrame with route geometries.
        
    Returns:
        folium.Map: A Folium map object.
    """
    
    # 1. Select the stop_times relevant to the filtered route_trips (using trip_id)
    route_stop_times = stop_times.merge(
        trips[['trip_id', 'shape_id']], 
        on='trip_id', 
        how='inner'
    )
    
    # 2. Get unique stop IDs used by this route
    unique_stop_ids = route_stop_times['stop_id'].unique().tolist()
    
    # 3. Filter the stops DataFrame to just the stops used by the route
    route_stops = stops[stops['stop_id'].isin(unique_stop_ids)].copy()
    
    # Check if we have any stops to plot
    if route_stops.empty:
        # Create a default map centered on Toronto
        m = folium.Map(location=[43.6532, -79.3832], zoom_start=12, tiles='CartoDB Positron')
        return m

    # 4. Initialize Folium Map centered on the average stop location
    avg_lat = route_stops['stop_lat'].mean()
    avg_lon = route_stops['stop_lon'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13, tiles='CartoDB Positron')
    
    # 5. Draw route lines from shapes data
    if not shapes.empty and 'shape_id' in route_stop_times.columns:
        # Get unique shape_ids for this route
        shape_ids = route_stop_times['shape_id'].dropna().unique()
        
        for shape_id in shape_ids:
            # Get all points for this shape
            shape_points = shapes[shapes['shape_id'] == shape_id].sort_values('shape_pt_sequence')
            
            if not shape_points.empty:
                # Create list of [lat, lon] coordinates
                coordinates = shape_points[['shape_pt_lat', 'shape_pt_lon']].values.tolist()
                
                # Draw the route line
                folium.PolyLine(
                    coordinates,
                    color='#3498db',
                    weight=4,
                    opacity=0.7
                ).add_to(m)
    
    # 6. Add BMO Field marker
    BMO_LAT, BMO_LON = 43.6331, -79.4184
    folium.Marker(
        [BMO_LAT, BMO_LON], 
        popup='BMO Field - World Cup 2026 Venue',
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)

    # 7. Add markers for each stop (on top of lines)
    for index, row in route_stops.iterrows():
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=5,
            color='#2c3e50',
            fill=True,
            fill_color='#3498db',
            fill_opacity=0.8,
            weight=2,
            tooltip=row['stop_name']
        ).add_to(m)
        
    return m
