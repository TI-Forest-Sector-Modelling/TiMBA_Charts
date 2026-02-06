import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from pathlib import Path
from Toolbox.classes.PlotManager import overviewplots

from Toolbox.parameters.default_parameters import (
    default_plot_settings,
    printing_plot_settings,
)

PACKAGEDIR = Path(__file__).parent.parent.absolute()


class OverviewDB:
    def __init__(self, app, data, print_settings=False, color_list=None):
        self.app = app
        self.data = data
        self.op = overviewplots()
        self.color_list = color_list or ["#1f77b4", "#ff7f0e", "#2ca02c"]
        self.start = data["year"].min()
        self.end = data["year"].max()

        self.plot_settings = (
            printing_plot_settings if print_settings else default_plot_settings
        )

        self.app_layout = self.create_layout()
        self.create_callbacks()

    def create_layout(self):
        dropdown_style = {'height': '25px', 'marginBottom': '5px'}

        app_layout = dbc.Container(
            fluid=True,
            className="p-2",
            style={
                'backgroundColor': 'white',
                'height': 'calc(100vh - 80px)',
                'display': 'flex',
                'flexDirection': 'column',
                'overflow': 'hidden'
            },
            children=[
                dbc.Row(
                    [
                        # ================= LEFT COLUMN =================
                        dbc.Col(
                            [
                                # === FILTER CARD ===
                                dbc.Card(
                                    className="shadow-sm",
                                    style={
                                        'backgroundColor': 'white',
                                        'padding': '15px',
                                        'height': '50%',
                                        'marginBottom': '0.5vh',
                                        'display': 'flex',
                                        'flexDirection': 'column'
                                    },
                                    children=[
                                        dbc.CardBody(
                                            style={
                                                'padding': '15px',
                                                'overflowY': 'auto',
                                                'flex': '1 1 auto',
                                                'display': 'flex',
                                                'flexDirection': 'column',
                                                'gap': '10px'
                                            },
                                            children=[
                                                html.H4("Filters", className="card-title mb-2"),

                                                dcc.Dropdown(
                                                    id='odb_region-dropdown',
                                                    options=[
                                                        {'label': i, 'value': i}
                                                        for i in sorted(self.data['ISO3'].dropna().unique())
                                                    ],
                                                    multi=True,
                                                    placeholder="Select Country...",
                                                    style=dropdown_style
                                                ),

                                                dcc.Dropdown(
                                                    id='odb_continent-dropdown',
                                                    options=[
                                                        {'label': i, 'value': i}
                                                        for i in sorted(self.data['Continent'].dropna().unique())
                                                    ],
                                                    multi=True,
                                                    placeholder="Select Continent...",
                                                    style=dropdown_style
                                                ),

                                                dcc.Dropdown(
                                                    id='odb_domain-dropdown',
                                                    options=[
                                                        {'label': i, 'value': i}
                                                        for i in sorted(self.data['domain'].dropna().unique())
                                                    ],
                                                    multi=True,
                                                    placeholder="Select Domain...",
                                                    style=dropdown_style
                                                ),

                                                dcc.Dropdown(
                                                    id='odb_commodity-dropdown',
                                                    options=[
                                                        {'label': i, 'value': i}
                                                        for i in sorted(self.data['Commodity'].dropna().unique())
                                                    ],
                                                    multi=True,
                                                    placeholder="Select Commodity...",
                                                    style=dropdown_style
                                                ),

                                                dcc.Dropdown(
                                                    id='odb_commodity-group-dropdown',
                                                    options=[
                                                        {'label': i, 'value': i}
                                                        for i in self.data['Commodity_Group'].dropna().unique().tolist()
                                                    ],
                                                    multi=True,
                                                    placeholder="Select Commodity Group...",
                                                    style=dropdown_style
                                                ),

                                                dcc.Dropdown(
                                                    id='odb_scenario-filter',
                                                    options=[
                                                        {'label': i, 'value': i}
                                                        for i in self.data['Scenario'].unique()
                                                    ],
                                                    multi=True,
                                                    placeholder="Select Scenario...",
                                                    style=dropdown_style
                                                ),

                                                html.Button(
                                                    "⬇️ CSV Export",
                                                    id="odb_btn_csv",
                                                    className="ml-auto btn btn-outline-secondary",
                                                    style={'borderRadius': '4px'}
                                                ),
                                                dcc.Download(id="odb_download-dataframe-csv"),
                                            ]
                                        )
                                    ]
                                ),

                                # === PRICE PLOT CARD ===
                                dbc.Card(
                                    className="shadow-sm",
                                    style={
                                        'backgroundColor': 'white',
                                        'padding': '15px',
                                        'height': '50%',
                                        'marginBottom': '0.25vh',
                                        'display': 'flex',
                                        'flexDirection': 'column'
                                    },
                                    children=[
                                        dbc.CardBody(
                                            style={
                                                'padding': '10px',
                                                'height': '100%',
                                                'display': 'flex',
                                                'flexDirection': 'column'
                                            },
                                            children=[
                                                dcc.Graph(
                                                    id='odb_price-plot',
                                                    config={
                                                        'toImageButtonOptions': {
                                                            'format': 'png',
                                                            'filename': 'price_plot',
                                                            'scale': 5
                                                        }
                                                    },
                                                    style={
                                                        'flex': '1 1 auto',
                                                        'height': '100%',
                                                        'width': '100%',
                                                        'minHeight': '250px'
                                                    }
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ],
                            width=3,
                            style={
                                'height': '100%',
                                'display': 'flex',
                                'flexDirection': 'column'
                            }
                        ),

                        # ================= RIGHT COLUMN =================
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        # === QUANTITY PLOT CARD ===
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    className="shadow-sm",
                                                    style={
                                                        "backgroundColor": "white",
                                                        "padding": "15px",
                                                        "height": "100%",
                                                        'marginBottom': '0.25vh',
                                                        "display": "flex",
                                                        "flexDirection": "column",
                                                    },
                                                    children=[
                                                        dbc.CardBody(
                                                            style={
                                                                "padding": "10px",
                                                                "flex": "1 1 auto",
                                                                "display": "flex",
                                                                "flexDirection": "column",
                                                            },
                                                            children=[
                                                                dcc.Graph(
                                                                    id="odb_quantity-plot",
                                                                    config={
                                                                        "toImageButtonOptions": {
                                                                            "format": "png",
                                                                            "filename": "quantity_plot",
                                                                            "scale": 5,
                                                                        }
                                                                    },
                                                                    style={
                                                                        "flex": "1 1 auto",
                                                                        "width": "100%",
                                                                        "minHeight": "250px",
                                                                    },
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                )
                                            ],
                                            width=8,
                                            style={"height": "100%"},
                                        ),

                                        # === FOREST + WORLD MAP ===
                                        dbc.Col(
                                            [
                                                # === FOREST STOCK ===
                                                dbc.Card(
                                                    className="shadow-sm",
                                                    style={
                                                        "backgroundColor": "white",
                                                        "padding": "15px",
                                                        "height": "50%",
                                                        "flex": "1 1 0",
                                                        "marginBottom": "0.5vh",
                                                        "display": "flex",
                                                        "flexDirection": "column",
                                                    },
                                                    children=[
                                                        dbc.CardBody(
                                                            style={
                                                                "padding": "15px",
                                                                "overflowY": "auto",
                                                                "flex": "1 1 auto",
                                                                "display": "flex",
                                                                "flexDirection": "column",
                                                            },
                                                            children=[
                                                                dcc.Graph(
                                                                    id="odb_forstock-plot",
                                                                    config={
                                                                        "toImageButtonOptions": {
                                                                            "format": "png",
                                                                            "filename": "forstock_plot",
                                                                            "scale": 5,
                                                                        }
                                                                    },
                                                                    style={
                                                                        "flex": "1 1 auto",
                                                                        "width": "100%",
                                                                        "minHeight": "250px",
                                                                    },
                                                                )
                                                            ],
                                                        )
                                                    ],
                                                ),

                                                # === WORLD MAP ===
                                                dbc.Card(
                                                    className="shadow-sm",
                                                    style={
                                                        "backgroundColor": "white",
                                                        "padding": "15px",
                                                        "height": "50%",
                                                        'marginBottom': '0.25vh',
                                                        "flex": "1 1 0",
                                                        "display": "flex",
                                                        "flexDirection": "column",
                                                    },
                                                    children=[
                                                        dbc.CardBody(
                                                            style={
                                                                "padding": "10px",
                                                                "flex": "1 1 auto",
                                                                "display": "flex",
                                                                "flexDirection": "column",
                                                            },
                                                            children=[
                                                                html.H5("Filter for Worldmap"),
                                                                dcc.Dropdown(
                                                                    id="odb_year-filter",
                                                                    options=[
                                                                        {"label": i, "value": i}
                                                                        for i in sorted(self.data["year"].unique())
                                                                    ],
                                                                    placeholder="Select Year...",
                                                                    style=dropdown_style,
                                                                ),
                                                                dcc.Graph(
                                                                    id="odb_world-map",
                                                                    config={
                                                                        "toImageButtonOptions": {
                                                                            "format": "png",
                                                                            "filename": "world_map",
                                                                            "scale": 5,
                                                                        }
                                                                    },
                                                                    style={
                                                                        "flex": "1 1 auto",
                                                                        "width": "100%",
                                                                        "minHeight": "250px",
                                                                    },
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            width=4,
                                            style={
                                                "display": "flex",
                                                "flexDirection": "column",
                                                "height": "100%",
                                            },
                                        ),
                                    ],
                                    style={"flex": "1 1 auto"},
                                )
                            ],
                            width=9,
                            style={
                                "height": "100%",
                                "display": "flex",
                                "flexDirection": "column",
                            },
                        ),
                    ],
                    style={"height": "calc(100% - 6.5vh)"},
                ),

                # ================= NAVIGATION =================
                dbc.Row(
                    [
                        dbc.Col(),
                        dbc.Col(
                            dbc.Button(
                                "Forest Dashboard →",
                                color="success",
                                href="/forest",
                                className="mt-1 mb-1 w-100",
                            ),
                            xs=6,
                            sm=6,
                            md=3,
                            className="ms-auto",
                        ),
                    ],
                    justify="between",
                    className="mt-auto mb-1",
                ),
            ],
        )

        return app_layout


    # ======================================================
    # FILTERING
    # ======================================================
    def filter_data(self, region, continent, domain, commodity, commodity_group, scenario):
        df = self.data.copy()

        if region:
            df = df[df["ISO3"].isin(region)]
        if continent:
            df = df[df["Continent"].isin(continent)]
        if domain:
            df = df[df["domain"].isin(domain)]
        if commodity:
            df = df[df["Commodity"].isin(commodity)]
        if commodity_group:
            df = df[df["Commodity_Group"].isin(commodity_group)]
        if scenario:
            df = df[df["Scenario"].isin(scenario)]

        return self.remove_extreme_outliers(df, "price")

    # ======================================================
    # CALLBACKS
    # ======================================================
    def create_callbacks(self):
        @self.app.callback(
            [
                Output("odb_quantity-plot", "figure"),
                Output("odb_price-plot", "figure"),
                Output("odb_forstock-plot", "figure"),
            ],
            [
                Input("odb_region-dropdown", "value"),
                Input("odb_continent-dropdown", "value"),
                Input("odb_domain-dropdown", "value"),
                Input("odb_commodity-dropdown", "value"),
                Input("odb_commodity-group-dropdown", "value"),
                Input("odb_scenario-filter", "value"),
            ],
        )
        def update_plots(region, continent, domain, commodity, commodity_group, scenario):
            filtered_data = self.filter_data(
                region=region,
                continent=continent,
                domain=domain,
                commodity=commodity,
                commodity_group=commodity_group,
                scenario=scenario,
            )

            if not isinstance(filtered_data, pd.DataFrame):
                raise TypeError(
                    f"filter_data muss DataFrame liefern, "
                    f"bekommen: {type(filtered_data)}"
                )
            
            title_suffix = self.generate_title(
                region,
                continent,
                domain,
                commodity,
                commodity_group,
            )

            fig_quantity = self.op.create_quantity_plot(
                filtered_data=filtered_data,
                start_year=self.start,
                end_year=self.end,
                color_list=self.color_list,
                plot_settings=self.plot_settings,
                title_suffix=title_suffix,
            )

            fig_price = self.op.create_price_plot(
                filtered_data=filtered_data,
                color_list=self.color_list,
            )

            fig_forstock = self.op.create_forstock_plot(
                filtered_data=filtered_data,
                color_list=self.color_list,
            )
            
            return fig_quantity, fig_price, fig_forstock


        @self.app.callback(
            Output("odb_world-map", "figure"),
            [
                Input("odb_scenario-filter", "value"),
                Input("odb_year-filter", "value"),
                Input("odb_region-dropdown", "value"),
                Input("odb_continent-dropdown", "value"),
                Input("odb_domain-dropdown", "value"),
                Input("odb_commodity-dropdown", "value"),
                Input("odb_commodity-group-dropdown", "value"),
            ],
        )
        def update_world_map(scenario, year, region, continent, domain, commodity, commodity_group):
            filtered = self.filter_data(
                region, continent, domain, commodity, commodity_group, scenario
            )

            if year:
                filtered = filtered[filtered["year"] == year]

            title_suffix = self.generate_title(
                region, continent, domain, commodity, commodity_group
            )

            return self.op.create_world_map_plot(filtered, title_suffix)

    # ======================================================
    # HELPERS
    # ======================================================
    def generate_title(self, region, continent, domain, commodity, commodity_group):
        parts = []
        for item in [region, continent, domain, commodity, commodity_group]:
            if item:
                parts.append(str(item))
        return ", ".join(parts).replace("[", "").replace("]", "").replace("'", "") or "all data"

    def remove_extreme_outliers(self, df, col, threshold=50):
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        limit = threshold * IQR
        df.loc[df[col] >= limit, col] = np.nan
        return df