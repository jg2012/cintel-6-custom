from pathlib import Path
import pandas as pd
from shiny import reactive
from shiny.express import render, ui, input
from ipyleaflet import Map, Marker, Popup
from shinywidgets import render_widget
import ipywidgets as widgets

# Define the path to the CSV file
infile = "alt_fuel_stations.csv"

# Function to read data from the CSV file
def dat():
    return pd.read_csv(infile)

# Sidebar UI setup
with ui.sidebar(id="sidebar_left", open="desktop"):
    ui.h2("Enter Zip Code")
    ui.input_text("zip_code", "Type a zip code")

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
                charging_stations = filtered_infile()  # Get the filtered data
                if not charging_stations.empty:
                    m = Map(center=(charging_stations.iloc[0]["Latitude"], charging_stations.iloc[0]["Longitude"]), zoom=10)
                    for index, row in charging_stations.iterrows():
                        marker = Marker(location=(row["Latitude"], row["Longitude"]))
                        
                        
                        
                        m.add_layer(marker)
                    # Set a fixed height for the map container
                    m.layout.height = "500px"
                    return m
                else:
                    # If no data is found for the inputted zip code, return an empty map
                    return Map(center=(37.0902, -95.7129), zoom=4)

# Reactive function to filter data based on zip code
@reactive.calc
def filtered_infile():
    selected_zip_code = input.zip_code()
    return dat()[dat()["ZIP"].isin([selected_zip_code])]
