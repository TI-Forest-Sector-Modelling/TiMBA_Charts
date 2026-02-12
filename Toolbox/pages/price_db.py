import dash
import pandas as pd
import numpy as np
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from Toolbox.classes.PlotManager import Plots, PlotUtils
from datetime import datetime


class PriceDB:

    def __init__(self, app, data: pd.DataFrame):
        self.app = app
        self.data = data
        self.plots = Plots()
        self.scenarios = sorted(self.data["Scenario"].dropna().unique())
        self.colors = PlotUtils().get_scenario_colors(self.scenarios)

        self.app_layout = self.create_layout()
        self.register_callbacks()

    # ------------------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------------------
    def create_layout(self):

        legend_items = [
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "margin": "0 14px"
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
                "paddingTop": "0px",
                "paddingLeft": "0px",
                "paddingRight": "0px"
            },
            children=[

            # ==========================================================
            # FILTER BAR + DOWNLOAD BUTTON
            # ==========================================================
            dbc.Card(
                className="border-1 shadow-sm mb-3",
                style={
                    "backgroundColor": "#f8f9fa",   # leichtes Grau (Bootstrap light)
                    "border": "1px solid #dee2e6",  # dezente Umrandung
                    "borderRadius": "1px"
                },
                body=True,
                children=[
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "10px",
                            "alignItems": "flex-end",
                            "width": "100%",
                            # "backgroundColor": "#f8f9fa",
                            # "border": "1px solid #dee2e6",
                            # "borderRadius": "8px",
                            # "padding": "12px",
                            # "transition": "all 0.2s ease"
                        },
                        children=[

                            html.Div(
                                dcc.Dropdown(
                                    id="fdb_continent-dropdown",
                                    options=[{"label": c, "value": c}
                                            for c in sorted(self.data["Continent"].dropna().unique())],
                                    multi=True,
                                    placeholder="Select Continent..."
                                ),
                                style={"flex": "3"}
                            ),

                            html.Div(
                                dcc.Dropdown(
                                    id="fdb_country-dropdown",
                                    options=[{"label": c, "value": c}
                                            for c in sorted(self.data["ISO3"].dropna().unique())],
                                    multi=True,
                                    placeholder="Select Country..."
                                ),
                                style={"flex": "3"}
                            ),

                            html.Div(
                                dcc.Dropdown(
                                    id="fdb_scenario-dropdown",
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
                                dcc.Dropdown(
                                    id="fdb_domain-dropdown",
                                    options=[{"label": c, "value": c}
                                            for c in sorted(self.data['domain'].dropna().unique())],
                                    multi=True,
                                    placeholder="Select Domain..."
                                ),
                                style={"flex": "3"}
                            ),

                            html.Div(
                                dcc.Dropdown(
                                    id="fdb_commodity-dropdown",
                                    options=[{"label": c, "value": c}
                                            for c in sorted(self.data['Commodity'].dropna().unique())],
                                    multi=True,
                                    placeholder="Select Commodity..."
                                ),
                                style={"flex": "3"}
                            ),

                            html.Div(
                                dcc.Dropdown(
                                    id="fdb_commodity-group-dropdown",
                                    options=[{"label": c, "value": c}
                                            for c in sorted(self.data['Commodity_Group'].dropna().unique())],
                                    multi=True,
                                    placeholder="Select Commodity Group..."
                                ),
                                style={"flex": "3"}
                            ),

                            html.Div(
                                dbc.Button(
                                    "⬇ CSV",
                                    id="fdb_download-btn",
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
            # 2x2 GRID
            # ==========================================================
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gridTemplateRows": "1fr 1fr",
                    "gap": "15px",
                    "padding": "15px",
                    "backgroundColor": "#f8f9fa",
                    "border": "1px solid #dee2e6",
                    "borderRadius": "6px",
                },
                children=[

                    html.Div(
                        dcc.Graph(id="g_value", style={"height": "350px"}),
                        style={
                            "backgroundColor": "white",
                            "border": "1px solid #e3e6ea",
                            "borderRadius": "6px",
                            "padding": "10px"
                        }
                    ),

                    html.Div(),

                    html.Div(
                        dcc.Graph(id="g_price", style={"height": "350px"}),
                        style={
                            "backgroundColor": "white",
                            "border": "1px solid #e3e6ea",
                            "borderRadius": "6px",
                            "padding": "10px"
                        }
                    ),

                    html.Div(),
                ]
            ),



            # ==========================================================
            # GLOBAL LEGEND
            # ==========================================================
            dbc.Card(
                className="border-0 mt-2",
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

            # Download Component
            dcc.Download(id="fdb_download")
        ])

    # ------------------------------------------------------------------
    # CALLBACKS
    # ------------------------------------------------------------------
    def register_callbacks(self):

        # ---------------------------
        # Plots aktualisieren
        # ---------------------------
        @self.app.callback(
            Output("g_value", "figure"),
            Output("g_price", "figure"),
            Input("fdb_continent-dropdown", "value"),
            Input("fdb_country-dropdown", "value"),
            Input("fdb_domain-dropdown", "value"),
            Input("fdb_commodity-dropdown", "value"),
            Input("fdb_commodity-group-dropdown", "value"),
            Input("fdb_scenario-dropdown", "value"),
        )
        def update_plots(continent, region, domain, commodity, commodity_group, scenario):
            df = PlotUtils.filter_data(
                df=self.data.copy(),
                region=region,
                continent=continent,
                domain=domain,
                commodity=commodity,
                commodity_group=commodity_group,
                scenario=scenario,
            )

            value_fig = self.plots.create_value_plot(df)
            price_fig = self.plots.create_price_plot(df)

            return value_fig, price_fig

        # ---------------------------
        # Download CSV
        # ---------------------------
        @self.app.callback(
            Output("fdb_download", "data"),
            Input("fdb_download-btn", "n_clicks"),
            State("fdb_continent-dropdown", "value"),
            State("fdb_country-dropdown", "value"),
            State("fdb_domain-dropdown", "value"),
            State("fdb_commodity-dropdown", "value"),
            State("fdb_commodity-group-dropdown", "value"),
            State("fdb_scenario-dropdown", "value"),
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

            # Dynamischer Dateiname
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"filtered_data_{timestamp}.csv"

            return dcc.send_data_frame(df.to_csv, filename, index=False)
