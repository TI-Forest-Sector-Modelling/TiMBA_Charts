import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from pathlib import Path
import Toolbox.parameters.default_parameters as dp
from Toolbox.classes.utils import PlotUtils
from Toolbox.classes.PlotManager import Plots
from Toolbox.classes.LayoutManager import Layout, FilterLayout
from Toolbox.parameters.filter_config import WORLD_MAP_DB_FILTERS,FOREST_DB_FILTERS
import Toolbox.parameters.layout_styles as ls
from datetime import datetime

PACKAGEDIR = Path(__file__).parent.parent.absolute()


class WorldMapDB:
     
    def __init__(self, 
                 app, 
                 data: pd.DataFrame,
                 df_stock: pd.DataFrame, 
                 df_area: pd.DataFrame ):
        self.app = app
        self.db_prefix = "wmdb"
        self.data = data
        self.df_stock = df_stock
        self.df_area=df_area
        self.plots = Plots()
        self.layout = Layout()
        self.filter_builder = FilterLayout(self.data, prefix=self.db_prefix)
        self.scenarios = sorted(self.data.columns[6:].unique())
        self.colors = PlotUtils().get_scenario_colors(self.scenarios)
        self.app_layout = self.create_layout()
        self.register_callbacks()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def create_layout(self):

        filters = self.filter_builder.build_all(WORLD_MAP_DB_FILTERS)

        return dbc.Container(
            fluid=True,
            style=ls.outer_card_under_header,
            # ==========================================================
            # Card for filter bar
            # ==========================================================
            children=[
                dbc.Card(
                    className="border-1 shadow-sm",
                    style=ls.filter_card_background,
                    body=True,
                    children=[
                        html.Div(
                            style=ls.filter_inner_card,
                            children = filters
                        )
                    ]
                ),
                # ==========================================================
                # Card behind all plots
                # ==========================================================
                html.Div(
                    style=ls.plot_card_3x2_background_simple,
                    children=[
                        #-----------
                        # Cards for the specific plots
                        #-----------
                        self.layout._graph_card("wmdb_world_map_supply"),
                        self.layout._graph_card("wmdb_world_map_manuf"),
                        self.layout._graph_card("wmdb_world_map_stock"),
                        #html.Div(),
                        self.layout._graph_card("wmdb_world_map_netexp"),
                        self.layout._graph_card("wmdb_world_map_demand"),
                        self.layout._graph_card("wmdb_world_map_area"),
                        #html.Div(),

                    ]
                ),

                # ==========================================================
                # Card for the legend
                # ==========================================================
                self.layout._legend_card_world_map(),
            ]
        )
    
    
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def register_callbacks(self):
        filter_inputs = PlotUtils().build_filter_inputs(self.db_prefix, WORLD_MAP_DB_FILTERS)


        @self.app.callback(
            Output("wmdb_world_map_supply", "figure"),
            Output("wmdb_world_map_manuf", "figure"),
            Output("wmdb_world_map_netexp", "figure"),
            Output("wmdb_world_map_demand", "figure"),
            Output("wmdb_world_map_stock", "figure"),
            Output("wmdb_world_map_area", "figure"),
            Output("wmdb_legend_scenario_text", "children"),
            *filter_inputs,
        )
        def update_plots(*filter_values):
            print(f"{self.db_prefix}_dashboard")
            filter_values_dict = dict(zip(WORLD_MAP_DB_FILTERS.keys(), filter_values))
            print(filter_values_dict)
            #-----------
            # add a filter world map
            #-----------
            pivot_df= PlotUtils.filter_data(
                df=self.data.copy(),
                **PlotUtils().get_plot_filters(
                    filter_values_dict, 
                    "worldmap"
                )
            )

            ref = filter_values_dict["refscenario"]
            alt = filter_values_dict["altscenario"]
            if not alt:
                alt = self.scenarios[0:1]
            if not ref:
                ref = self.scenarios[0:1]
            ref = ref[0]
            alt = alt[0]

            print("REF:", ref)
            print("ALT:", alt)

            pivot_df["diff"] = pivot_df[alt]-pivot_df[ref]
            pivot_df["diff"]= pivot_df["diff"].replace([np.inf, -np.inf, -1], np.nan)
            pivot_df = pivot_df.dropna(subset=['diff']).reset_index(drop=True)

            pivot_df = pivot_df.groupby(["ISO3","domain"])[["diff"]].sum().reset_index()

            df_map_s = pivot_df[pivot_df["domain"] == "Supply"]
            world_map_supply = self.plots.create_diff_world_map_plot(
                df_map_s,
                title="Supply"
            )

            df_map_m = pivot_df[pivot_df["domain"] == "Manufacturing"]
            world_map_manuf = self.plots.create_diff_world_map_plot(
                df_map_m,
                title="Manufacturing"
            )

            df_map_n = pivot_df[pivot_df["domain"] == "Net Exports"]
            world_map_netexp = self.plots.create_diff_world_map_plot(
                df_map_n,
                title="Net Exports"
            )

            df_map_d = pivot_df[pivot_df["domain"] == "Demand"]
            world_map_demand = self.plots.create_diff_world_map_plot(
                df_map_d,
                title="Demand"
            )

            #-----------
            # subset forest stock data
            #-----------
            df_stock = PlotUtils.filter_data(
                df=self.df_stock.copy(),
                **PlotUtils().get_plot_filters(
                    filter_values_dict, 
                    "worldmap_forest"
                )
            )

            df_stock["diff"] = df_stock[alt]-df_stock[ref]
            df_stock["diff"]= df_stock["diff"].replace([np.inf, -np.inf, -1], np.nan)
            df_stock = df_stock.dropna(subset=['diff']).reset_index(drop=True)

            world_map_stock = self.plots.create_diff_world_map_plot(
                df_stock,
                title="Forest Stock"
            )

            #-----------
            # subset forest area data
            #-----------
            df_area = PlotUtils.filter_data(
                df=self.df_area.copy(),
                **PlotUtils().get_plot_filters(
                    filter_values_dict, 
                    "worldmap_forest"
                )
            )

            df_area["diff"] = df_area[alt] - df_area[ref]
            df_area["diff"]= df_area["diff"].replace([np.inf, -np.inf, -1], np.nan)
            df_area = df_area.dropna(subset=['diff']).reset_index(drop=True)

            world_map_area = self.plots.create_diff_world_map_plot(
                df_area,
                title="Forest Area"
            )

            legend_text = f"Reference: {ref} | Alternative: {alt}"

            return (
                world_map_supply,
                world_map_manuf,
                world_map_netexp,
                world_map_demand,
                world_map_stock,
                world_map_area,
                legend_text
            )