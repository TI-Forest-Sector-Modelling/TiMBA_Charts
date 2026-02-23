import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
from Toolbox.classes.utils import PlotUtils
from Toolbox.classes.PlotManager import Plots
from Toolbox.classes.LayoutManager import Layout, FilterLayout
from Toolbox.parameters.filter_config import TRADE_DB_FILTERS
import Toolbox.parameters.layout_styles as ls
from datetime import datetime


class BiTradeDB:
     
    def __init__(self, 
                 app, 
                 data: pd.DataFrame,
                 colors):
        self.app = app
        self.db_prefix = "tdb"
        self.data = data
        self.filters = TRADE_DB_FILTERS
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
                    style=ls.plot_card_3x2_background_simple,
                    children=[
                        #-----------
                        # Cards for the specific plots
                        #-----------

                        self.layout._graph_card("tbd_import_q"),
                        self.layout._graph_card("tbd_export_q"),
                        self.layout._graph_card("tbd_net_export_q"),
                        self.layout._graph_card("tbd_import_v"),
                        self.layout._graph_card("tbd_export_v"),
                        self.layout._graph_card("tbd_net_export_v"),

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
            Output("tbd_import_q", "figure"),
            Output("tbd_export_q", "figure"),
            Output("tbd_net_export_q", "figure"),
            Output("tbd_import_v", "figure"),
            Output("tbd_export_v", "figure"),
            Output("tbd_net_export_v", "figure"),
            *filter_inputs,
        )
        def update_plots(*filter_values):
            print(f"{self.db_prefix}_dashboard")
            filter_values_dict = dict(zip(self.filters.keys(), filter_values))
            print(filter_values_dict)
            #-----------
            # subset for net export
            #-----------
            df = PlotUtils.filter_data(
                df=self.data.copy(),
                **PlotUtils().get_plot_filters(
                    filter_values_dict, 
                    "trade"
                )
            )
            q_import_fig = self.plots.create_trade_line_plot(
                df,
                "Import",
                "quantity",
                colors=self.colors
            )
            q_export_fig = self.plots.create_trade_line_plot(
                df,
                "Export",
                "quantity",
                colors=self.colors
            )
            q_net_export_fig = self.plots.create_trade_bar_plot(
                df,
                "Net Exports",
                "quantity",
                colors=self.colors
            )
            v_import_fig = self.plots.create_trade_line_plot(
                df,
                "Import",
                "Value",
                colors=self.colors
            )
            v_export_fig = self.plots.create_trade_line_plot(
                df,
                "Export",
                "Value",
                colors=self.colors
            )
            v_net_export_fig = self.plots.create_trade_bar_plot(
                df,
                "Net Exports",
                "Value",
                colors=self.colors
            )

            return q_import_fig,q_export_fig,q_net_export_fig,v_import_fig,v_export_fig,v_net_export_fig

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
        