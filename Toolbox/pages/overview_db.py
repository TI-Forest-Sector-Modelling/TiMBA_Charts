import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from pathlib import Path
import Toolbox.parameters.default_parameters as dp
from Toolbox.classes.PlotManager import Plots, PlotUtils
from datetime import datetime

from Toolbox.parameters.default_parameters import (
    default_plot_settings,
    printing_plot_settings,
)

PACKAGEDIR = Path(__file__).parent.parent.absolute()


class OverviewDB:
     
    def __init__(self, app, data: pd.DataFrame):
        self.app = app
        self.data = data[dp.overview_db]
        self.forest_df = data[dp.forest_db]
        self.plots = Plots()
        self.plot_utils = PlotUtils()
        self.scenarios = sorted(self.data["Scenario"].dropna().unique())
        self.colors = PlotUtils().get_scenario_colors(self.scenarios)
        self.app_layout = self.create_layout()
        self.register_callbacks()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def create_layout(self):

        legend_items = [
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "margin": "0 14px",
                },
                children=[
                    html.Div(
                        style={
                            "width": "14px",
                            "height": "14px",
                            "backgroundColor": self.colors[s],
                            "marginRight": "6px"
                        }
                    ),
                    html.Span(s)
                ]
            )
            for s in self.scenarios
        ]

        return dbc.Container(
            fluid=True,
            style={
                "height": "calc(100vh - 175px)",   #header = 140 pxl, dazu etwas spielraum
                "display": "flex",
                "flexDirection": "column",
                "padding": "0px",
                "overflow": "hidden"
            },
            children=[

                # ==========================================================
                # Card for filter bar
                # ==========================================================
                dbc.Card(
                    className="border-1 shadow-sm",
                    style={
                        "backgroundColor": "#f8f9fa",
                        "border": "1px solid #dee2e6",
                        "borderRadius": "1px",
                        "flexShrink": "0"   # ⭐ Nie schrumpfen
                    },
                    body=True,
                    children=[
                        html.Div(
                            style={
                                "display": "flex",
                                "gap": "10px",
                                "alignItems": "flex-end",
                                "width": "100%",
                            },
                            children=[

                                html.Div(
                                    dcc.Dropdown(
                                        id="odb_continent-dropdown",
                                        options=[{"label": c, "value": c}
                                                for c in sorted(self.data["Continent"].dropna().unique())],
                                        multi=True,
                                        placeholder="Select Continent..."
                                    ),
                                    style={"flex": "3"}
                                ),

                                html.Div(
                                    dcc.Dropdown(
                                        id="odb_country-dropdown",
                                        options=[{"label": c, "value": c}
                                                for c in sorted(self.data["ISO3"].dropna().unique())],
                                        multi=True,
                                        placeholder="Select Country..."
                                    ),
                                    style={"flex": "3"}
                                ),

                                html.Div(
                                    dcc.Dropdown(
                                        id="odb_domain-dropdown",
                                        options=[{"label": c, "value": c}
                                                for c in sorted(self.data['domain'].dropna().unique())],
                                        multi=True,
                                        placeholder="Select Domain..."
                                    ),
                                    style={"flex": "3"}
                                ),

                                html.Div(
                                    dcc.Dropdown(
                                        id="odb_commodity-dropdown",
                                        options=[{"label": c, "value": c}
                                                for c in sorted(self.data['Commodity'].dropna().unique())],
                                        multi=True,
                                        placeholder="Select Commodity..."
                                    ),
                                    style={"flex": "3"}
                                ),

                                html.Div(
                                    dcc.Dropdown(
                                        id="odb_commodity-group-dropdown",
                                        options=[{"label": c, "value": c}
                                                for c in sorted(self.data['Commodity_Group'].dropna().unique())],
                                        multi=True,
                                        placeholder="Select Commodity Group..."
                                    ),
                                    style={"flex": "3"}
                                ),
                                
                                html.Div(
                                    dcc.Dropdown(
                                        id="odb_scenario-dropdown",
                                        options=[{"label": "All", "value": "All"}] + [
                                            {"label": s, "value": s}
                                            for s in self.scenarios
                                        ],
                                        multi=True,
                                        placeholder="Select Scenario..."
                                    ),
                                    style={"flex": "3"}
                                ),

                                html.Div(
                                    dbc.Button(
                                        "⬇ CSV",
                                        id="odb_download-btn",
                                        color="primary",
                                        style={"height": "38px"}
                                    ),
                                    style={"flex": "1"}
                                ),
                            ]
                        )
                    ]
                ),
                # ==========================================================
                # Card behind all plots
                # ==========================================================
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1fr 1.75fr 1fr",
                        "gridTemplateRows": "1fr 1fr",
                        "gap": "15px",
                        "padding": "15px",
                        "backgroundColor": "#f8f9fa",
                        "border": "1px solid #dee2e6",
                        "borderRadius": "6px",
                        "marginTop": "10px",
                        "marginBottom": "10px",
                        "flexGrow": "1",
                        "minHeight": "0",
                        "height": "100%"
                    },
                    children=[
                        #-----------
                        # Cards for the specific plots
                        #-----------
                        self.plot_utils._graph_card("odb_q_net_export_fig"),
                        html.Div(
                            self.plot_utils._graph_card("odb_main_plot"),
                            style={
                                "gridColumn": "2",
                                "gridRow": "1 / span 2",
                                "height": "100%", 
                                "minHeight": "0",  
                            }
                        ),
                        self.plot_utils._graph_card("odb_forstock_plot"),
                        self.plot_utils._graph_card("odb_price_plot"),
                        self.plot_utils._graph_card("odb_world_map"),

                    ]
                ),

                # ==========================================================
                # Card for the legend
                # ==========================================================
                dbc.Card(
                    className="border-1 shadow-sm",
                    style={
                        "padding": "5px",
                        "backgroundColor": "#f8f9fa",
                        "border": "1px solid #dee2e6",
                        "borderRadius": "1px",
                        "flexShrink": "0"
                    },
                    body=True,
                    children=[
                        html.Div(
                            legend_items,
                            style={
                                "display": "flex",
                                "justifyContent": "center",
                                "flexWrap": "wrap"
                            }
                        )
                    ]
                ),

                dcc.Download(id="odb_download")
            ]
        )
    
    
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def register_callbacks(self):
        @self.app.callback(
            Output("odb_main_plot", "figure"),
            Output("odb_price_plot", "figure"),
            Output("odb_q_net_export_fig", "figure"),
            Output("odb_forstock_plot", "figure"),
            Output("odb_world_map", "figure"),
            Input("odb_continent-dropdown", "value"),
            Input("odb_country-dropdown", "value"),
            Input("odb_domain-dropdown", "value"),
            Input("odb_commodity-dropdown", "value"),
            Input("odb_commodity-group-dropdown", "value"),
            Input("odb_scenario-dropdown", "value"),
        )
        def update_plots(continent, region, domain, commodity, commodity_group, scenario):
            
            #-----------
            # subset for net export
            #-----------
            df = PlotUtils.filter_data(
                df=self.data.copy(),
                region=region,
                continent=continent,
                commodity=commodity,
                commodity_group=commodity_group,
                scenario=scenario,
            )
            q_net_export_fig = self.plots.create_trade_bar_plot(df,"Net Exports","quantity")

            #-----------
            # add additional filter for main and price plot
            #-----------
            df = PlotUtils.filter_data(
                df=df,
                domain=domain,
            )
            main_plot = self.plots.create_quantity_plot(df)
            price_plot = self.plots.create_price_growth_plot(df=df)

            #-----------
            # add a filter world map
            #-----------
            df = df[df["Scenario"]=="Historic Data"]
            max_year=df["year"].max()
            df = PlotUtils.filter_data(
                df=df,
                year=[max_year],
            )
            world_map = self.plots.create_world_map_plot(df,max_year=max_year)

            #-----------
            # subset forest data
            #-----------
            forest_df = PlotUtils.filter_data(
                df=self.forest_df.copy(),
                region=region,
                continent=continent,
                scenario=scenario,
            )
            forstock_plot = self.plots.plot_forstock(forest_df)

            return main_plot, price_plot, q_net_export_fig, forstock_plot, world_map

        # ---------------------------
        # Download CSV
        # ---------------------------
        @self.app.callback(
            Output("odb_download", "data"),
            Input("odb_download-btn", "n_clicks"),
            State("odb_continent-dropdown", "value"),
            State("odb_country-dropdown", "value"),
            State("odb_domain-dropdown", "value"),
            State("odb_commodity-dropdown", "value"),
            State("odb_commodity-group-dropdown", "value"),
            State("odb_scenario-dropdown", "value"),
            prevent_initial_call=True
        )
        def download_filtered_csv(n_clicks, continent, region, domain, commodity, commodity_group, scenario):
            if n_clicks is None:
                return dash.no_update

            df = PlotUtils.filter_data(
                df=self.data.copy(),
                region=region,
                continent=continent,
                domain=domain,
                commodity=commodity,
                commodity_group=commodity_group,
                scenario=scenario
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"filtered_data_{timestamp}.csv"

            return dcc.send_data_frame(df.to_csv, filename, index=False)
