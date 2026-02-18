import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
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
     
    def __init__(self, app, data: pd.DataFrame):
        self.app = app
        self.db_prefix = "wmdb"
        self.data = data[dp.overview_db]
        self.forest_df = data[dp.forest_db]
        self.plots = Plots()
        self.layout = Layout()
        self.filter_builder = FilterLayout(self.data, prefix=self.db_prefix)
        self.scenarios = sorted(self.data["Scenario"].dropna().unique())
        self.colors = PlotUtils().get_scenario_colors(self.scenarios)
        self.app_layout = self.create_layout()
        self.register_callbacks()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def create_layout(self):

        filters = self.filter_builder.build_all(WORLD_MAP_DB_FILTERS)
        button = self.layout.download_button()

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
                            children = filters + button
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
                self.layout._legend_card(colors= self.colors,
                                         scenarios = self.scenarios),
                dcc.Download(id="wmdb_download")
            ]
        )
    
    
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def register_callbacks(self):
        filter_inputs = PlotUtils().build_filter_inputs(self.db_prefix, WORLD_MAP_DB_FILTERS)
        print(filter_inputs)

        @self.app.callback(
            Output("wmdb_world_map_supply", "figure"),
            Output("wmdb_world_map_manuf", "figure"),
            Output("wmdb_world_map_netexp", "figure"),
            Output("wmdb_world_map_demand", "figure"),
            Output("wmdb_world_map_stock", "figure"),
            Output("wmdb_world_map_area", "figure"),
            *filter_inputs,
        )
        def update_plots(*filter_values):
            filter_values_dict = dict(zip(WORLD_MAP_DB_FILTERS.keys(), filter_values))
            #-----------
            # add a filter world map
            #-----------
            try:
                df_map, ref, alt = PlotUtils.filter_data(
                    df=self.data.copy(),
                    **PlotUtils().get_plot_filters(
                        filter_values_dict, 
                        "worldmap"
                    )
                )
            except ValueError:
                df_map = PlotUtils.filter_data(
                    df=self.data.copy(),
                    **PlotUtils().get_plot_filters(
                        filter_values_dict, 
                        "worldmap"
                    )
                )

            pivot_df = (
                df_map.groupby(["ISO3", "Scenario", "domain","year","Commodity","Commodity_Group"])["quantity"]
                .sum()
                .unstack("Scenario", fill_value=0)
                .reset_index()
            )
            ref = ref[0]
            alt=alt[0]
            pivot_df["diff"] = pivot_df[ref] / pivot_df[alt] -1
            pivot_df = pivot_df[["ISO3","domain","year","Commodity","Commodity_Group",ref,alt,"diff"]]
            pivot_df = pivot_df.dropna(subset=['diff']).reset_index(drop=True)

            max_year = pivot_df["year"].max()
            pivot_df = PlotUtils.filter_data(
                df=pivot_df,
                year=[max_year]
            )

            df_map_s = pivot_df[pivot_df["domain"] == "Supply"]
            world_map_supply = self.plots.create_diff_world_map_plot(
                df_map_s,
                max_year=max_year,
                column="diff"
            )

            df_map_m = pivot_df[pivot_df["domain"] == "Manufacturing"]
            world_map_manuf = self.plots.create_diff_world_map_plot(
                df_map_m,
                max_year=max_year,
                column="diff"
            )

            df_map_n = pivot_df[pivot_df["domain"] == "Net Exports"]
            world_map_netexp = self.plots.create_diff_world_map_plot(
                df_map_n,
                max_year=max_year,
                column="diff"
            )

            df_map_d = pivot_df[pivot_df["domain"] == "Demand"]
            world_map_demand = self.plots.create_diff_world_map_plot(
                df_map_d,
                max_year=max_year,
                column="diff"
            )

            #-----------
            # subset forest data
            #-----------
            forest_filter_values_dict = dict(zip(FOREST_DB_FILTERS.keys(), filter_values))

            df_forest = PlotUtils.filter_data(
                df=self.forest_df.copy(),
                **PlotUtils().get_plot_filters(
                    forest_filter_values_dict, 
                    "forest"
                )
            )
            world_map_stock = self.plots.create_diff_world_map_plot(
                df_forest,
                max_year=max_year,
                column="ForStock"
            )
            world_map_area = self.plots.create_diff_world_map_plot(
                df_forest,
                max_year=max_year,
                column="ForArea"
            )

            return (
                world_map_supply, 
                world_map_manuf, 
                world_map_netexp, 
                world_map_demand, 
                world_map_stock, 
                world_map_area
            )

        # # ---------------------------
        # # Download CSV
        # # ---------------------------
        # filter_states = [
        #     State(f"odb_{key}-dropdown", "value")
        #     for key in OVERVIEW_DB_FILTERS.keys()
        # ]

        # @self.app.callback(
        #     Output("odb_download", "data"),
        #     Input("odb_download-btn", "n_clicks"),
        #     *filter_states,
        #     prevent_initial_call=True
        # )

        # def download_filtered_csv(n_clicks, *filter_values):
        #     if n_clicks is None:
        #         return dash.no_update
            
        #     filter_values_dict = dict(zip(OVERVIEW_DB_FILTERS.keys(), filter_values))

        #     df = PlotUtils.filter_data(
        #         df=self.data.copy(),
        #         **filter_values_dict
        #     )

        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        #     return dcc.send_data_frame(
        #         df.to_csv,
        #         f"filtered_data_{timestamp}.csv",
        #         index=False
        #     )
        