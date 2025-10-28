import sys
from pathlib import Path

# --- Project Root Setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# --- Imports ---
import streamlit as st
import folium
import json
from src.data_load import load_gtfs_tables
from src.processing import trips_per_day, stops_per_route, get_mode_mapping, get_routes_by_mode, calculate_headway_stats
from src.maps import plot_route_map

# --- Streamlit Page Config ---
st.set_page_config(page_title="TTC Dashboard", layout="wide")
st.title("World Cup Transit Impact - Toronto 2026 ⚽")
st.markdown(
    """
    I was one of the lucky lottery winners for the 2026 World Cup ticket draw (**actually** my mom was - thanks mom!), and I managed to score tickets to see team Canada play in Toronto.

    As a big public transit fan/advocate, I of course plan to take Toronto public transit to and from the game. I wanted to understand how ready Toronto's transit system is for the 6 games they're hosting.

    This tool establishes a **Scheduled Reliability Baseline** for routes serving the BMO Field (World Cup 2026 venue). 
    
    By analyzing the static GTFS schedule data, we identify where the *planned* service has inconsistent **Headways** (time between vehicles). These locations are pre-existing schedule vulnerabilities that will amplify into 
    major bottlenecks, gapping, and bunching under high ridership demand.
    """
)

# --- Data Loading & Caching ---
@st.cache_data(show_spinner=False)
def get_data():
    """Load all GTFS data tables once and cache them."""
    return load_gtfs_tables()

st.write("Loading GTFS data...")
stops, routes, trips, stop_times, calendar = get_data() # Using cached load

# --- Mode Mapping & Options ---
MODE_MAPPING = get_mode_mapping()
MODE_NAMES = {v: k for k, v in MODE_MAPPING.items()}
available_mode_codes = routes['route_type'].unique()
available_mode_options = [MODE_MAPPING[code] for code in available_mode_codes if code in MODE_MAPPING]
default_mode_name = MODE_MAPPING.get(700, available_mode_options[0] if available_mode_options else None)

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Mode filter
selected_mode_name = st.sidebar.selectbox(
    "Select Mode of Transit", 
    options=available_mode_options,
    index=available_mode_options.index(default_mode_name) if default_mode_name in available_mode_options else 0
)
selected_mode_code = MODE_NAMES[selected_mode_name]

# Route filter (dependent on mode)
available_routes = get_routes_by_mode(routes, selected_mode_code)
if not available_routes:
    st.warning(f"No routes found for the selected mode: **{selected_mode_name}**.")
    st.stop()
route_id = st.sidebar.selectbox("Select Route", options=available_routes)

day = st.sidebar.selectbox("Select Day", ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])

# Load Toronto World Cup games 
with open(PROJECT_ROOT / "data" / "toronto_world_cup_games.json", "r") as f:
    world_cup_games = json.load(f)

# --- World Cup Game Selection ---
st.sidebar.header("World Cup Game")
game_labels = [f"Match {g['match']} - {g['teams']} ({g['date']} {g['time']})" for g in world_cup_games]
selected_game_idx = st.sidebar.selectbox("Select World Cup Game", options=range(len(game_labels)), format_func=lambda i: game_labels[i])
selected_game = world_cup_games[selected_game_idx]

# --- Attendance Slider ---
st.sidebar.header("Expected Attendance")
attendance = st.sidebar.slider(
    "Set expected stadium attendance",
    min_value=10000,
    max_value=60000,
    value=45000,
    step=1000
)

# --- Time Window Filter ---
st.sidebar.header("Time Window")
st.sidebar.markdown("Filter analysis to high-demand periods (e.g., post-game departures).")
time_start = st.sidebar.time_input("Start Time (HH:MM)", value=None, key='start_time')
time_end = st.sidebar.time_input("End Time (HH:MM)", value=None, key='end_time')
start_time_str = time_start.strftime("%H:%M:%S") if time_start else None
end_time_str = time_end.strftime("%H:%M:%S") if time_end else None

# --- Data Filtering & Headway Analysis ---
daily_trips = trips_per_day(trips, calendar, day.lower())
route_trips = daily_trips[daily_trips['route_id'] == route_id]

if route_trips.empty:
    st.warning(f"No trips found for Route {route_id} on {day}.")
    m = folium.Map(location=[43.6532, -79.3832], zoom_start=12)
    st.components.v1.html(m._repr_html_(), height=600)
    st.stop()
else:
    st.write(f"Total trips for route {route_id} on {day}: **{route_trips.shape[0]}**")
    # Calculate headway stats using time filters
    headway_stats_df = calculate_headway_stats(
        route_trips, stop_times, stops,
        start_time_filter=start_time_str,
        end_time_filter=end_time_str
    )
    if headway_stats_df.empty:
        time_window_message = f" between {start_time_str} and {end_time_str}" if start_time_str and end_time_str else ""
        st.error(f"Could not calculate Headway Stats. No trips found{time_window_message} for this selection.")
        m = folium.Map(location=[43.6532, -79.3832], zoom_start=12)
        st.components.v1.html(m._repr_html_(), height=600)
        st.stop()

# --- Route Info & Main Content ---
# Get and format the human-readable route name
route_info = routes[routes['route_id'] == route_id].iloc[0]
route_long_name_raw = route_info['route_long_name']
route_long_name_formatted = route_long_name_raw.title()

st.write(f"Analyzing Route **{route_id} - {route_long_name_formatted}** ({selected_mode_name}) on **{day}**.")

# Stops per route
num_stops_dict = stops_per_route(route_trips, stop_times)
num_stops = num_stops_dict.get(route_id, 0)
st.write(f"Total stops for route {route_id}: **{num_stops}**")

# --- Map Visualization ---
m = plot_route_map(route_trips, stop_times, stops, headway_stats_df)
st.components.v1.html(m._repr_html_(), height=600)