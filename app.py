from pathlib import Path
import pandas as pd  # Add this import statement
from shiny import reactive
from shiny.express import render, ui, input
from ipyleaflet import Map , Marker
from shinywidgets import render_widget 

ui.page_opts(title="EV Charging Stations in the U.S.")
ui.page_opts(fillable=True)

# Read the .csv
infile = Path(__file__).parent / "alt_fuel_stations.csv"

def dat():
    return pd.read_csv(infile)

with ui.sidebar(id="sidebar_left", open="desktop"):
    "Select Your State"
    ui.input_selectize("state", "Choose a state", [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ], multiple=True)

with ui.layout_columns(fillable=True):
    with ui.layout_columns():
        with ui.card(width=6):
            ui.card_header("Charging Station Data")
            @render.data_frame
            def render_penguins_table():
                return filtered_infile()
        with ui.card(width=6):  
            @render_widget
            def map():
                m = Map(center=(37.0902, -95.7129), zoom=4)
                charging_stations = filtered_infile()  # Get the filtered data
                for index, row in charging_stations.iterrows():
                    marker = Marker(location=(row["Latitude"], row["Longitude"]))
                    m.add_layer(marker)
                return m

@reactive.calc
def filtered_infile():
    selected_states = input.state()
    return dat()[dat()["State"].isin(selected_states)]

