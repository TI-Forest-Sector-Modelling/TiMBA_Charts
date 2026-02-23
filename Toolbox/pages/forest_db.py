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
from Toolbox.parameters.filter_config import FOREST_DB_FILTERS
import Toolbox.parameters.layout_styles as ls
from datetime import datetime

PACKAGEDIR = Path(__file__).parent.parent.absolute()


class ForestDB:
     
    def __init__(self,app,data: pd.DataFrame,colors):
        self.app = app
        self.db_prefix = "fdb"
        self.data = data
        self.plots = Plots()
        self.layout = Layout()
        self.filter_builder = FilterLayout(self.data, prefix=self.db_prefix)
        self.filters = FOREST_DB_FILTERS
        self.scenarios = sorted(self.data["Scenario"].dropna().unique())
        self.colors = colors
        self.app_layout = self.create_layout()
        self.register_callbacks()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def create_layout(self):

        filters = self.filter_builder.build_all(self.filters)
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

                        self.layout._graph_card("fdb_forarea_plot"),
                        self.layout._graph_card("fdb_area_growth_plot"),
                        self.layout._graph_card("fdb_stock_area_ratio_plot"),
                        self.layout._graph_card("fdb_forstock_plot"),
                        self.layout._graph_card("fdb_stock_growth_plot"),
                        self.layout._graph_card("fdb_supply_from_forest_plot"),

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
            Output("fdb_forarea_plot", "figure"),
            Output("fdb_area_growth_plot", "figure"),
            Output("fdb_stock_area_ratio_plot", "figure"),
            Output("fdb_forstock_plot", "figure"),
            Output("fdb_stock_growth_plot", "figure"),
            Output("fdb_supply_from_forest_plot", "figure"),
            *filter_inputs,
        )
        def update_plots(*filter_values):
            print(f"{self.db_prefix}_dashboard")
            filter_values_dict = dict(zip(self.filters.keys(), filter_values))
            print(filter_values_dict)
            #-----------
            # subset forest data
            #-----------
            forest_filter_values_dict = dict(zip(
                self.filters.keys(), 
                filter_values
                )
            )

            df = PlotUtils.filter_data(
                df=self.data.copy(),
                **PlotUtils().get_plot_filters(
                    forest_filter_values_dict, 
                    "forest"
                )
            )

            f_forarea=self.plots.plot_forarea(df,colors=self.colors)
            f_forstock=self.plots.plot_forstock(df,colors=self.colors)
            f_area_growth=self.plots.plot_area_growth(df,colors=self.colors)
            f_stock_growth=self.plots.plot_stock_growth(df,colors=self.colors)
            f_stock_area_ratio=self.plots.plot_stock_area_ratio(df,colors=self.colors)
            f_supply_from_forest=self.plots.plot_supply_from_forest(df,colors=self.colors)

            return (f_forarea, f_area_growth, f_stock_area_ratio,
                    f_forstock, f_stock_growth, f_supply_from_forest)
        # ---------------------------
        # Download CSV
        # ---------------------------
        filter_states = [
            State(f"{self.db_prefix}_{key}-dropdown", "value")
            for key in self.filters.keys()
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
        