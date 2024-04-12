from pathlib import Path
import pandas as pd
from shiny import reactive
from shiny.express import render, ui, input
from ipyleaflet import Map, Marker
from shinywidgets import render_widget
import matplotlib.pyplot as plt  


ui.page_opts(title="EV Charging Stations in the U.S.", fillable=True)

# Defines path and reads CSV file 
def dat():
    infile = Path(__file__).parent.joinpath("alt_fuel_stations.csv")
    return pd.read_csv(infile)


# Sidebar UI setup
with ui.sidebar(id="sidebar_left", open="desktop"):
    ui.HTML('<h3 style="font-size: medium;">Filter Options</h3>')
    with ui.accordion():
        with ui.accordion_panel("Filter by City"):
            cities = sorted(map(str, dat()["City"].unique().tolist()))
            ui.input_selectize("city_names", "Select Cities", choices=cities, multiple=True)
        with ui.accordion_panel("Filter by State"):
            states = sorted(map(str, dat()["State"].unique().tolist()))
            ui.input_selectize("state_names", "Select States", choices=states, multiple=True)

    
# Main UI layout setup
with ui.layout_columns(fillable=True):
    with ui.layout_columns():
        with ui.card(width=6, style="background-color: lightgray"):
            ui.card_header("Charging Station Data")
            @render.data_frame
            def render_charging_stations_table():
                return filtered_infile()

        with ui.card(width=6, style="background-color: lightgray"):
            @render_widget
            def show_map():
                charging_stations = filtered_infile()
                if not charging_stations.empty:
                    zoom_level = 10
                    if len(charging_stations) > 1:
                        zoom_level = 4
                    m = Map(center=(charging_stations.iloc[0]["Latitude"], charging_stations.iloc[0]["Longitude"]), zoom=zoom_level)
                    for index, row in charging_stations.iterrows():
                        marker = Marker(location=(row["Latitude"], row["Longitude"]))
                        m.add_layer(marker)
                    m.layout.height = "500px"
                    return m
                else:
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
        return pd.DataFrame(columns=dat().columns)

# Render bar graph for total charging stations by city or state
with ui.card(width=12, style="background-color: lightgray"):
    ui.card_header("Total Charging Stations by City or State")
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