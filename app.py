from pathlib import Path
import pandas
from shiny import reactive
from shiny.express import render, ui

ui.page_opts(title="EV Charging Stations in the U.S.")

ui.page_opts(fillable=True)

with ui.sidebar(id="sidebar_left", open="desktop"):
        "Select Your State"

with ui.layout_columns(fillable=True):
            def dat():
                infile = Path(__file__).parent/"alt_fuel_stations.csv"
                return pandas.read_csv(infile)

            with ui.navset_card_underline():

                with ui.nav_panel("Data frame"):
                    @render.data_frame
                    def frame():
                    # Give dat() to render.DataGrid to customize the grid
                        return dat()

        

