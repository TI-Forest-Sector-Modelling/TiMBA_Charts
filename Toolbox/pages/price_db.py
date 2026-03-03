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
from Toolbox.parameters.filter_config import PRICE_DB_FILTERS
import Toolbox.parameters.layout_styles as ls
from datetime import datetime

PACKAGEDIR = Path(__file__).parent.parent.absolute()


class PriceDB:
     
    def __init__(self, 
                 app, 
                 data: pd.DataFrame,
                 colors):
        self.app = app
        self.db_prefix = "pdb"
        self.data = data
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
        filters = self.filter_builder.build_all(PRICE_DB_FILTERS)
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
                    style=ls.plot_card_2x2_background_simple,
                    children=[
                        #-----------
                        # Cards for the specific plots
                        #-----------
                        self.layout._graph_card("g_value"),
                        self.layout._graph_card("g_value_growh"),
                        self.layout._graph_card("g_price"),
                        self.layout._graph_card("g_price_growth"),

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
        filter_inputs = PlotUtils().build_filter_inputs(self.db_prefix, PRICE_DB_FILTERS)

        @self.app.callback(
            Output("g_value", "figure"),
            Output("g_value_growh", "figure"),
            Output("g_price", "figure"),
            Output("g_price_growth", "figure"),
            *filter_inputs,
        )
        def update_plots(*filter_values):
            print(f"{self.db_prefix}_dashboard")
            filter_values_dict = dict(zip(PRICE_DB_FILTERS.keys(), filter_values))
            print(filter_values_dict)
            #-----------
            # subset for net export
            #-----------
            df = PlotUtils.filter_data(
                df=self.data.copy(),
                **PlotUtils().get_plot_filters(
                    filter_values_dict, 
                    "main"
                )
            )

            title = PlotUtils.generate_title(
                filter_dict=filter_values_dict,
            )

            agg_df = (
                df.groupby(["Scenario", "Period", "year"], as_index=False)
                .agg({
                    "Value": "sum",
                    "quantity": "sum"
                })
            )

            value_fig = self.plots.create_value_plot(
                df, 
                colors=self.colors,
                title=title,
            )
            value_growth_fig = self.plots.create_value_growth_plot(
                agg_df, 
                colors=self.colors,
                title=title,
            )
            price_fig = self.plots.create_price_plot(
                agg_df, 
                colors=self.colors,
                title=title,
            )
            price_growth_fig = self.plots.create_price_growth_plot(
                agg_df, 
                colors=self.colors,
                title=title,
            )

            return value_fig, value_growth_fig, price_fig, price_growth_fig
        # ---------------------------
        # Download CSV
        # ---------------------------
        filter_states = [
            State(f"{self.db_prefix}_{key}-dropdown", "value")
            for key in PRICE_DB_FILTERS.keys()
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
            
            filter_values_dict = dict(zip(PRICE_DB_FILTERS.keys(), filter_values))

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
        