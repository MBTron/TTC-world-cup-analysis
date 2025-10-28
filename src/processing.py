import pandas as pd

def get_mode_mapping():
    """
    Returns a mapping of TTC GTFS route_type codes to mode names.
    """
    return {
        900: "Streetcar",  # TTC uses 900 for Streetcar (standard GTFS uses 0)
        400: "Subway",          # TTC uses 400 for Subway (standard GTFS uses 1)
        700: "Bus",                     # TTC uses 700 for Bus (standard GTFS uses 3)
    }

def trips_per_day(trips, calendar, day="monday"):
    """
    Filters trips for a given day of the week using the calendar table.
    """
    service_ids = calendar[calendar[day]==1]['service_id']
    daily_trips = trips[trips['service_id'].isin(service_ids)]
    return daily_trips

def stops_per_route(daily_trips, stop_times):
    """
    Returns a dictionary of route_id to number of unique stops served for each route.
    """
    merged = daily_trips.merge(stop_times, on="trip_id")
    return merged.groupby("route_id")['stop_id'].nunique().to_dict()

def get_routes_by_mode(routes, selected_mode_code) -> list: 
    """
    Returns a list of route_ids for the selected mode code.
    """
    return routes[routes['route_type'] == selected_mode_code]['route_id'].unique().tolist()

def calculate_headway_stats(trips_df, stop_times_df, stops_df, start_time_filter=None, end_time_filter=None): 
    """
    Calculates the average & median scheduled headway (time b/w consecutive trips) for every stop on a given route. 
    Returns a DataFrame with stop-level statistics.
    """

    # 1. merge trips and stop_times to link route, trip, and time 
    df = stop_times_df.merge(
        trips_df[['trip_id', 'route_id', 'service_id']], 
        on='trip_id', 
        how='inner'
    )

    # 2. convert time to seconds since midnight for doing math stuff 
    def time_to_seconds(time_str):
        if pd.isna(time_str):
            return 0 
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    
    df['arrival_time_sec'] = df['arrival_time'].apply(time_to_seconds)

    # OPTIONAL TIME WINDOW FILTERING
    if start_time_filter and end_time_filter:
        start_sec = time_to_seconds(start_time_filter)
        end_sec = time_to_seconds(end_time_filter)

        if not (pd.isna(start_sec) or pd.isna(end_sec)):
            # filter out DF to include only trips in widow 
            df = df[
                (df['arrival_time_sec'] >= start_sec) & 
                (df['arrival_time_sec'] <= end_sec)
            ].copy()
            
            # check if trips left after filter
            if df.empty:
                return pd.DataFrame()

    # 3. sort by service_id (day) and stop_id, then time
    df = df.sort_values(['service_id', 'stop_id', 'arrival_time_sec'])

    # 4. calculate headway
    # Group by stop_id and service_id, then calculate the difference between current arrival time...
    # and previous arrival time (shift(1))
    df['previous_arrival_time_sec'] = df.groupby(['stop_id', 'service_id'])['arrival_time_sec'].shift(1)
    
    df['headway_sec'] = df['arrival_time_sec'] - df['previous_arrival_time_sec']

    # Filter out the first stop in each group (which will have a NaN for headway)
    # Also filters out trips that are the first one in the filtered time window
    headways = df.dropna(subset=['headway_sec'])

    # 5. aggregate to get stop-level statistics
    stop_stats = headways.groupby('stop_id').agg(
        avg_headway_minutes=('headway_sec', lambda x: x.mean() / 60),
        median_headway_minutes=('headway_sec', lambda x: x.median() / 60),
        total_trips_served=('trip_id', 'count')
    ).reset_index()

    # 6. Add stop names for display
    # Only merge if we have stats to merge
    if not stop_stats.empty:
        stop_stats = stop_stats.merge(
            stops_df[['stop_id', 'stop_name']], 
            on='stop_id', 
            how='left'
        ).drop_duplicates(subset=['stop_id'])

    return stop_stats