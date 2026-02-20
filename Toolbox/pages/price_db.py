import dash
import pandas as pd
import numpy as np
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from Toolbox.classes.PlotManager import Plots, PlotUtils
from datetime import datetime


class PriceDB:

    def __init__(self, app, data: pd.DataFrame,colors:dict):
        self.app = app
        self.data = data
        self.plots = Plots()
        self.scenarios = sorted(self.data["Scenario"].dropna().unique())
        self.colors = colors

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
                # FILTER BAR
                # ==========================================================
                dbc.Card(
                    className="border-1 shadow-sm",
                    style={
                        "backgroundColor": "#f8f9fa",
                        "border": "1px solid #dee2e6",
                        "borderRadius": "1px",
                        "flexShrink": "0"
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
                                        id="pdb_continent-dropdown",
                                        options=[{"label": c, "value": c}
                                                for c in sorted(self.data["Continent"].dropna().unique())],
                                        multi=True,
                                        placeholder="Select Continent..."
                                    ),
                                    style={"flex": "3"}
                                ),

                                html.Div(
                                    dcc.Dropdown(
                                        id="pdb_country-dropdown",
                                        options=[{"label": c, "value": c}
                                                for c in sorted(self.data["ISO3"].dropna().unique())],
                                        multi=True,
                                        placeholder="Select Country..."
                                    ),
                                    style={"flex": "3"}
                                ),

                                html.Div(
                                    dcc.Dropdown(
                                        id="pdb_scenario-dropdown",
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
                                        id="pdb_domain-dropdown",
                                        options=[{"label": c, "value": c}
                                                for c in sorted(self.data['domain'].dropna().unique())],
                                        multi=True,
                                        placeholder="Select Domain..."
                                    ),
                                    style={"flex": "3"}
                                ),

                                html.Div(
                                    dcc.Dropdown(
                                        id="pdb_commodity-dropdown",
                                        options=[{"label": c, "value": c}
                                                for c in sorted(self.data['Commodity'].dropna().unique())],
                                        multi=True,
                                        placeholder="Select Commodity..."
                                    ),
                                    style={"flex": "3"}
                                ),

                                html.Div(
                                    dcc.Dropdown(
                                        id="pdb_commodity-group-dropdown",
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
                                        id="pdb_download-btn",
                                        color="primary",
                                        style={"height": "38px"}
                                    ),
                                    style={"flex": "1"}
                                ),
                            ]
                        )
                    ]
                ),

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
                        "marginTop": "10px",
                        "marginBottom": "10px",
                        "flexGrow": "1",
                        "minHeight": "0"
                    },
                    children=[

                        self._graph_card("g_value"),
                        self._graph_card("g_value_growh"),
                        self._graph_card("g_price"),
                        self._graph_card("g_price_growth"),

                    ]
                ),

                # ==========================================================
                # LEGEND
                # ==========================================================
                dbc.Card(
                    className="border-1 shadow-sm",
                    style={
                        "padding": "5px",
                        "backgroundColor": "#f8f9fa",
                        "border": "1px solid #dee2e6",
                        "borderRadius": "1px",
                        "flexShrink": "0"   # ⭐ Immer sichtbar
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

                dcc.Download(id="pdb_download")
            ]
        )
    
    def _graph_card(self, graph_id):
        return html.Div(
            dcc.Graph(
                id=graph_id,
                style={"height": "100%"},
                config={"responsive": True}
            ),
            style={
                "display": "flex",
                "flexDirection": "column",
                "backgroundColor": "white",
                "border": "1px solid #e3e6ea",
                "borderRadius": "6px",
                "padding": "10px",
                "minHeight": "0"
            }
        )
    
    # ------------------------------------------------------------------
    # CALLBACKS
    # ------------------------------------------------------------------
    def register_callbacks(self):
        @self.app.callback(
            Output("g_value", "figure"),
            Output("g_value_growh", "figure"),
            Output("g_price", "figure"),
            Output("g_price_growth", "figure"),
            Input("pdb_continent-dropdown", "value"),
            Input("pdb_country-dropdown", "value"),
            Input("pdb_domain-dropdown", "value"),
            Input("pdb_commodity-dropdown", "value"),
            Input("pdb_commodity-group-dropdown", "value"),
            Input("pdb_scenario-dropdown", "value"),
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

            agg_df = (
                df.groupby(["Scenario", "Period", "year"], as_index=False)
                .agg({
                    "Value": "sum",
                    "quantity": "sum"
                })
            )

            value_fig = self.plots.create_value_plot(df, colors=self.colors)
            value_growth_fig = self.plots.create_value_growth_plot(agg_df, colors=self.colors)
            price_fig = self.plots.create_price_plot(agg_df, colors=self.colors)
            price_growth_fig = self.plots.create_price_growth_plot(agg_df, colors=self.colors)

            return value_fig, value_growth_fig, price_fig, price_growth_fig

        # ---------------------------
        # Download CSV
        # ---------------------------
        @self.app.callback(
            Output("pdb_download", "data"),
            Input("pdb_download-btn", "n_clicks"),
            State("pdb_continent-dropdown", "value"),
            State("pdb_country-dropdown", "value"),
            State("pdb_domain-dropdown", "value"),
            State("pdb_commodity-dropdown", "value"),
            State("pdb_commodity-group-dropdown", "value"),
            State("pdb_scenario-dropdown", "value"),
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

