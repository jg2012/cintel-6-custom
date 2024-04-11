from pathlib import Path
import pandas as pd
from shiny import reactive
from shiny.express import render, ui, input
from ipyleaflet import Map, Marker, Popup
from shinywidgets import render_widget
import ipywidgets as widgets

ui.page_opts(title="EV Charging Stations", fillable=True)

# Define the path to the CSV file
infile = "alt_fuel_stations.csv"

# Function to read data from the CSV file
def dat():
    return pd.read_csv(infile)

# Sidebar UI setup
with ui.sidebar(id="sidebar_left", open="desktop"):
    ui.h2("Filter Options")
    cities = sorted(map(str, dat()["City"].unique().tolist()))  # Get unique city names, convert to strings, and sort
    ui.input_selectize("city_names", "Select Cities", choices=cities, multiple=True)
    states = sorted(map(str, dat()["State"].unique().tolist()))  # Get unique state names, convert to strings, and sort
    ui.input_selectize("state_names", "Select States", choices=states, multiple=True)


with ui.card(width=6):
    ui.card_header("Total Charging Stations")
    @render.text
    def total_charging_stations():
        charging_stations = filtered_infile()
        total_stations = len(charging_stations)
        return total_stations

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
                    zoom_level = 10
                    if len(charging_stations) > 1:
                        zoom_level = 4
                    m = Map(center=(charging_stations.iloc[0]["Latitude"], charging_stations.iloc[0]["Longitude"]), zoom=zoom_level)
                    for index, row in charging_stations.iterrows():
                        marker = Marker(location=(row["Latitude"], row["Longitude"]))
                        m.add_layer(marker)
                    # Set a fixed height for the map container
                    m.layout.height = "500px"
                    return m
                else:
                    # If no data is found for the inputted filters, return an empty map
                    return Map(center=(37.0902, -95.7129), zoom=4)

# Reactive function to filter data based on selected cities and states
@reactive.calc
def filtered_infile():
    selected_cities = input.city_names()
    selected_states = input.state_names()
    if selected_cities:
        return dat()[dat()["City"].isin(selected_cities)]
    elif selected_states:
        return dat()[dat()["State"].isin(selected_states)]
    else:
        # If neither cities nor states are selected, return an empty DataFrame
        return pd.DataFrame(columns=dat().columns)

# Render bar graph for total charging stations by city or state
with ui.card(width=12):
    ui.card_header("Charging Stations by City or State")
    @render.plot
    def charging_stations_bar_plot():
        charging_stations = filtered_infile()
        if not charging_stations.empty:
            if input.city_names():
                grouped_data = charging_stations.groupby("City").size().reset_index(name="Total Stations")
                x_label = "City"
            else:
                grouped_data = charging_stations.groupby("State").size().reset_index(name="Total Stations")
                x_label = "State"
            plot = grouped_data.plot(x=x_label, y="Total Stations", kind="bar", legend=None)
            plot.set_ylabel("Total Charging Stations")
            plot.set_xlabel(x_label)
            for index, value in enumerate(grouped_data["Total Stations"]):
                plot.text(index, value + 0.1, str(value), ha='center', va='bottom')
            return plot.figure
        else:
            return None
