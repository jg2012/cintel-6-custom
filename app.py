from pathlib import Path
import pandas as pd
from shiny import reactive
from shiny.express import render, ui, input
from ipyleaflet import Map, Marker
from shinywidgets import render_widget
from ipywidgets import interact
import ipywidgets as widgets
import matplotlib.pyplot as plt
import seaborn as sns
import math
from geopy.geocoders import Nominatim

# Define the path to the CSV file
infile = "alt_fuel_stations.csv"

# Function to read data from the CSV file
def dat():
    return pd.read_csv(infile)

# Function to get latitude and longitude from a zip code
def get_coordinates(zip_code):
    geolocator = Nominatim(user_agent="charging_station_locator")
    location = geolocator.geocode(zip_code)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Function to calculate distance between two coordinates using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # Distance in kilometers
    return distance * 0.621371  # Convert distance to miles

# Sidebar UI setup
with ui.sidebar(id="sidebar_left", open="desktop"):
    ui.h2("Enter Zip Code")
    ui.input_text("zip_code", "Type a zip code")

    ui.h2("Select Maximum Distance (miles)")
    distance_slider = ui.input_slider("max_distance", label="Maximum Distance", min=5, max=50, step=5, value=25)



# Main UI layout setup
with ui.layout_columns(fillable=True):
    with ui.layout_columns():
        with ui.card(width=6):
            ui.card_header("Charging Station Data")
            @render.data_frame
            def render_charging_stations_table():
                return filtered_infile()  # Render filtered data

        with ui.card(width=6):
            @render_widget
            def show_map():
                m = Map(center=(37.0902, -95.7129), zoom=4)
                charging_stations = filtered_infile()  # Get the filtered data
                for index, row in charging_stations.iterrows():
                    marker = Marker(location=(row["Latitude"], row["Longitude"]))
                    m.add_layer(marker)
                return m

# Reactive function to filter data based on zip code and maximum distance
@reactive.calc
def filtered_infile():
    selected_zip_code = input.zip_code()
    max_distance = input.max_distance()
    
    zip_latitude, zip_longitude = get_coordinates(selected_zip_code)
    if zip_latitude is None or zip_longitude is None:
        return pd.DataFrame()  # Return empty DataFrame if coordinates are not found
    
    stations = dat()
    stations["Distance"] = stations.apply(lambda x: haversine(x["Latitude"], x["Longitude"], zip_latitude, zip_longitude), axis=1)
    # Filter stations within the maximum distance
    filtered_stations = stations[(stations["Distance"] <= max_distance) & (stations["ZIP"] == selected_zip_code)]
    return filtered_stations
