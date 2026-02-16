import dash
import pandas as pd
import numpy as np
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from Toolbox.classes.PlotManager import Plots, PlotUtils
from datetime import datetime


class ForestDB:

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

                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1fr 1fr 1fr",
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

                        self._graph_card("plot_forarea"),
                        self._graph_card("plot_forstock"),
                        self._graph_card("plot_area_growth"),
                        self._graph_card("plot_stock_growth"),
                        self._graph_card("plot_stock_area_ratio"),
                        self._graph_card("plot_supply_from_forest"),

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

                dcc.Download(id="fdb_download")
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
            Output("plot_forarea", "figure"),
            Output("plot_forstock", "figure"),
            Output("plot_area_growth", "figure"),
            Output("plot_stock_growth", "figure"),
            Output("plot_stock_area_ratio", "figure"),
            Output("plot_supply_from_forest", "figure"),
            Input("fdb_continent-dropdown", "value"),
            Input("fdb_country-dropdown", "value"),
            Input("fdb_scenario-dropdown", "value"),
        )
        def update_plots(continent, region, scenario):
            df = PlotUtils.filter_data(
                df=self.data.copy(),
                region=region,
                continent=continent,
                scenario=scenario,
            )
            plot_forarea=self.plots.plot_forarea(df)
            plot_forstock=self.plots.plot_forstock(df)
            plot_area_growth=self.plots.plot_area_growth(df)
            plot_stock_growth=self.plots.plot_stock_growth(df)
            plot_stock_area_ratio=self.plots.plot_stock_area_ratio(df)
            plot_supply_from_forest=self.plots.plot_supply_from_forest(df)

            return (plot_forarea,plot_forstock,plot_area_growth,
                    plot_stock_growth,plot_stock_area_ratio,plot_supply_from_forest)

        # ---------------------------
        # Download CSV
        # ---------------------------
        @self.app.callback(
            Output("fdb_download", "data"),
            Input("fdb_download-btn", "n_clicks"),
            State("fdb_continent-dropdown", "value"),
            State("fdb_country-dropdown", "value"),
            State("fdb_scenario-dropdown", "value"),
            prevent_initial_call=True
        )
        def download_filtered_csv(n_clicks, continent, region, scenario):
            if n_clicks is None:
                return dash.no_update

            df = PlotUtils.filter_data(
                df=self.data.copy(),
                region=region,
                continent=continent,
                scenario=scenario
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"filtered_data_{timestamp}.csv"

            return dcc.send_data_frame(df.to_csv, filename, index=False)
