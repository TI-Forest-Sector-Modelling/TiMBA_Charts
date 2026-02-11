import dash
import pandas as pd
import numpy as np
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from Toolbox.classes.PlotManager import Plots, PlotUtils


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

        return dbc.Container(fluid=True, children=[

            # ==========================================================
            # FILTER BAR
            # ==========================================================
            dbc.Card(
                className="border-0 shadow-sm mb-2",
                body=True,
                children=[
                    dbc.Row(className="g-3", children=[

                        dbc.Col(
                            dcc.Dropdown(
                                id="fdb_continent-dropdown",
                                options=[
                                    {"label": c, "value": c}
                                    for c in sorted(self.data["Continent"].dropna().unique())
                                ],
                                multi=True,
                                placeholder="Continent"
                            ),
                            width=4
                        ),

                        dbc.Col(
                            dcc.Dropdown(
                                id="fdb_country-dropdown",
                                options=[
                                    {"label": c, "value": c}
                                    for c in sorted(self.data["ISO3"].dropna().unique())
                                ],
                                multi=True,
                                placeholder="Country (ISO3)"
                            ),
                            width=4
                        ),

                        dbc.Col(
                            dcc.Dropdown(
                                id="fdb_scenario-dropdown",
                                options=[{"label": "All", "value": "All"}] + [
                                    {"label": s, "value": s}
                                    for s in self.scenarios
                                ],
                                multi=True,
                                placeholder="Scenario"
                            ),
                            width=4
                        ),
                    ])
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
                    "gap": "10px"
                },
                children=[
                    dcc.Graph(id="g_value"),   # links oben
                    html.Div(),                # rechts oben (leer)
                    dcc.Graph(id="g_price"),   # links unten  ✅ NEU
                    html.Div(),                # rechts unten (leer)
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
            )
        ])

    # ------------------------------------------------------------------
    # CALLBACKS
    # ------------------------------------------------------------------
    def register_callbacks(self):

        @self.app.callback(
        Output("g_value", "figure"),
        Output("g_price", "figure"),   # ✅ NEU
        Input("fdb_scenario-dropdown", "value"),
        Input("fdb_country-dropdown", "value"),
        Input("fdb_continent-dropdown", "value"),
        )

        def update_plots(scenarios, countries, continents):

            df = self.data.copy()

            df = PlotUtils.filter_data(
                df=df,
                region=countries,
                continent=continents,
                scenario=scenarios,
            )

            value_fig = self.plots.create_value_plot(df)
            price_fig = self.plots.create_price_plot(df)

            return value_fig, price_fig

