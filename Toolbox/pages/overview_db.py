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
from Toolbox.parameters.filter_config import OVERVIEW_DB_FILTERS,FOREST_DB_FILTERS
import Toolbox.parameters.layout_styles as ls
from datetime import datetime


class OverviewDB:
     
    def __init__(self, 
                 app, 
                 data: pd.DataFrame,
                 colors):
        self.app = app
        self.db_prefix = "odb"
        self.data = data[dp.overview_db]
        self.forest_df = data[dp.forest_db]
        self.filters = OVERVIEW_DB_FILTERS
        self.plots = Plots()
        self.layout = Layout()
        self.filter_builder = FilterLayout(self.data, prefix=self.db_prefix)
        self.scenarios = sorted(self.data["Scenario"].dropna().unique())
        self.colors = colors
        self.app_layout = self.create_layout()
        self.register_callbacks()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def create_layout(self):

        filters = self.filter_builder.build_all(self.filters)
        button = self.layout.download_button(f"{self.db_prefix}_download-btn")

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
                    style=ls.plot_card_3x2_background_main,
                    children=[
                        #-----------
                        # Cards for the specific plots
                        #-----------
                        self.layout._graph_card("odb_q_net_export_fig"),
                        html.Div(
                            self.layout._graph_card("odb_main_plot"),
                            style=ls.main_plot_card
                        ),
                        self.layout._graph_card("odb_forstock_plot"),
                        self.layout._graph_card("odb_price_plot"),
                        self.layout._graph_card("odb_world_map"),

                    ]
                ),

                # ==========================================================
                # Card for the legend
                # ==========================================================
                self.layout._legend_card(colors= self.colors,
                                         scenarios = self.scenarios),
                dcc.Download(id=f"{self.db_prefix}_download")
            ]
        )
    
    
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def register_callbacks(self):
        filter_inputs = PlotUtils().build_filter_inputs(
            self.db_prefix, 
            self.filters
        )

        @self.app.callback(
            Output("odb_main_plot", "figure"),
            Output("odb_price_plot", "figure"),
            Output("odb_q_net_export_fig", "figure"),
            Output("odb_forstock_plot", "figure"),
            Output("odb_world_map", "figure"),
            *filter_inputs,
        )
        def update_plots(*filter_values):
            print(f"{self.db_prefix}_dashboard")
            filter_values_dict = dict(zip(
                self.filters.keys(), 
                filter_values
                )
            )
            print(filter_values_dict)
            #-----------
            # subset forest data
            #-----------
            forest_filter_values_dict = dict(zip(
                FOREST_DB_FILTERS.keys(), 
                filter_values
                )
            )
            #print(forest_filter_values_dict)
            for_title = PlotUtils.generate_title(
                filter_dict=forest_filter_values_dict,
                ignore_keys=["commodity","commodity_group"]
            )

            df_forest = PlotUtils.filter_data(
                df=self.forest_df.copy(),
                **PlotUtils().get_plot_filters(
                    forest_filter_values_dict, 
                    "forest"
                )
            )
            # create forest stock plot
            forstock_plot = self.plots.plot_forstock(
                df_forest,
                colors=self.colors,
                title=for_title
            )

            #-----------
            # subset for net export
            #-----------
            df_trade = PlotUtils.filter_data(
                df=self.data.copy(),
                **PlotUtils().get_plot_filters(
                    filter_values_dict, 
                    "trade"
                )
            )
            y_label = PlotUtils.dynamic_y_label(df=df_trade)

            trade_title = PlotUtils.generate_title(
                filter_dict=filter_values_dict,
                ignore_keys=["domain"],
            )
            # create net export plot
            q_net_export_fig = self.plots.create_trade_bar_plot(
                df_trade,
                "Net Exports",
                "quantity",
                colors=self.colors,
                title=trade_title,
                y_label=y_label,
            )

            #-----------
            # add additional filter for main and price plot
            #-----------
            df_main = PlotUtils.filter_data(
                df=self.data.copy(),
                **PlotUtils().get_plot_filters(
                    filter_values_dict, 
                    "main"
                )
            )

            title = PlotUtils.generate_title(filter_dict=filter_values_dict)

            # create main plot          
            main_plot = self.plots.create_quantity_plot(
                df_main,
                colors=self.colors,
                title=title,
                y_label=y_label,
            )

            agg_df = (
                df_main.groupby(["Scenario", "Period", "year"], as_index=False)
                .agg({
                    "Value": "sum",
                    "quantity": "sum"
                })
            )
            
            # create price plot 
            price_plot = self.plots.create_price_growth_plot(
                agg_df,
                colors=self.colors,
                title=title
            )

            #-----------
            # add a filter world map
            #-----------
            df_map = PlotUtils.filter_data(
                df=self.data.copy(),
                **PlotUtils().get_plot_filters(
                    filter_values_dict, 
                    "map"
                )
            )

            df_map = df_map[df_map["Scenario"] == "Historic Data"]
            df_map = df_map[df_map["year"] == df_map["year"].max()]

            # create world map plot 
            world_map = self.plots.create_world_map_plot(
                df_map,
                max_year=df_map["year"].max(),
                title=title,
                colorbar_label=y_label
            )

            return main_plot, price_plot, q_net_export_fig, forstock_plot, world_map

        # ---------------------------
        # Download CSV
        # ---------------------------
        filter_states = [
            State(f"{self.db_prefix}_{key}-dropdown", "value")
            for key in OVERVIEW_DB_FILTERS.keys()
        ]

        @self.app.callback(
            Output(f"{self.db_prefix}_download", "data"),
            Input(f"{self.db_prefix}_download-btn", "n_clicks"),
            *filter_states,
            prevent_initial_call=True
        )

        def download_filtered_csv(n_clicks, *filter_values):
            if n_clicks is None:
                return dash.no_update
            
            filter_values_dict = dict(zip(self.filters.keys(), filter_values))

            df = PlotUtils.filter_data(
                df=self.data.copy(),
                **filter_values_dict
            )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            return dcc.send_data_frame(
                df.to_csv,
                f"filtered_data_{timestamp}.csv",
                index=False
            )
        