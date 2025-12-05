import dash
import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc
from Toolbox.parameters.default_parameters import default_plot_settings, printing_plot_settings


class TradeDB:
    def __init__(self, app, data: pd.DataFrame = None, print_settings: bool = False, color_list: list = None):
        self.app = app
        self.data = data
        self.app_layout = self.create_layout()
        self.color_list = color_list
        if print_settings:
            self.plot_settings = printing_plot_settings
        else:
            self.plot_settings = default_plot_settings

    def create_layout(self):
        dropdown_style = {
            'height': '38px',
            'marginRight': '10px',
            'flex': '1 1 220px',
            'minWidth': '180px'
        }

        app_layout = dbc.Container(
            fluid=True,
            className="p-2",
            style={
                'backgroundColor': 'white',
                'height': 'calc(100vh - 80px)',  # Adapting to the hight of the navigation header
                'display': 'flex',
                'flexDirection': 'column',
                'overflow': 'hidden'
            },
            children=[

                # ==== FILTER BAR ====
                dbc.Row([
                    dbc.Col([
                        dbc.Card(
                            className="border-0 shadow-sm",
                            style={'backgroundColor': '#f8f9fa'},
                            children=[
                                dbc.CardBody(
                                    style={'padding': '10px'},
                                    children=[
                                        html.Div(
                                            style={
                                                'display': 'flex',
                                                'flexWrap': 'wrap',
                                                'gap': '10px',
                                                'alignItems': 'center'
                                            },
                                            children=[
                                                dcc.Dropdown(
                                                    id='tdb_continent-dropdown',
                                                    options=[{'label': i, 'value': i}
                                                             for i in sorted(self.data['Continent'].dropna().unique())],
                                                    multi=True,
                                                    placeholder='Select Continent...',
                                                    style=dropdown_style
                                                ),
                                                dcc.Dropdown(
                                                    id='tdb_region-dropdown',
                                                    options=[{'label': 'Europe', 'value': 'Europe'},
                                                             {'label': 'Asia', 'value': 'Asia'}],
                                                    multi=True,
                                                    placeholder='Select Region...',
                                                    style=dropdown_style
                                                ),
                                                dcc.Dropdown(
                                                    id='tdb_country-dropdown',
                                                    options=[{'label': i, 'value': i}
                                                             for i in sorted(self.data['ISO3'].dropna().unique())],
                                                    multi=True,
                                                    placeholder='Select Country...',
                                                    style=dropdown_style
                                                ),
                                                dcc.Dropdown(
                                                    id='tdb_estimate-dropdown',
                                                    options=[
                                                        {'label': 'Forest Area', 'value': 'Forest Area'},
                                                        {'label': 'Forest Stock', 'value': 'Forest Stock'},
                                                        {'label': 'Harvest Intensity', 'value': 'Harvest Intensity'}
                                                    ],
                                                    multi=True,
                                                    placeholder='Select Estimate...',
                                                    style=dropdown_style
                                                ),
                                                dcc.Dropdown(
                                                    id='tdb_scenario-dropdown',
                                                    options=[{'label': 'All', 'value': 'All'}] +
                                                            [{'label': i, 'value': i}
                                                             for i in sorted(self.data['Scenario'].dropna().unique())],
                                                    multi=True,
                                                    placeholder='Select Scenario...',
                                                    style=dropdown_style
                                                ),
                                                html.Button(
                                                    "⬇️ CSV Export",
                                                    id="tdb_btn_csv",
                                                    className="ml-auto btn btn-outline-secondary",
                                                    style={
                                                        'height': '38px',
                                                        'marginLeft': 'auto',
                                                        'padding': '0 15px',
                                                        'borderRadius': '4px',
                                                    }
                                                ),
                                                dcc.Download(id="tdb_download-dataframe-csv")
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ])
                ], className="mb-3"),

                # ==== MAIN CONTENT (scrollable area below navbar) ====
                dbc.Row(
                    [
                        # LEFT COLUMN
                        dbc.Col(
                            dbc.Card(
                                className="shadow-sm h-100",
                                style={
                                    'backgroundColor': 'white',
                                    'padding': '15px',
                                    'display': 'flex',
                                    'flexDirection': 'column',
                                    'height': '100%'
                                },
                                children=[
                                    html.H5("Trade Placeholder Lineplot", className="card-title mb-3"),
                                    dcc.Graph(id='tdb_trend-graph', figure={},
                                              style={'flex': '1', 'minHeight': '300px'})
                                ]
                            ),
                            md=6, xs=12, className="mb-1",
                            style={'display': 'flex', 'flexDirection': 'column'}
                        ),

                        # RIGHT COLUMN
                        dbc.Col(
                            html.Div(
                                children=[
                                    dbc.Card(
                                        className="shadow-sm",
                                        style={
                                            'backgroundColor': 'white',
                                            'padding': '15px',
                                            'height': 'calc(50% - 0.5vh)',
                                            'marginBottom': '0.5vh',
                                            'display': 'flex',
                                            'flexDirection': 'column'
                                        },
                                        children=[
                                            html.H5("Trade Placeholder Barplot", className="card-title mb-3"),
                                            dcc.Graph(
                                                id='tdb_region-graph',
                                                figure={},
                                                style={'flex': '1', 'minHeight': '250px'}
                                            )
                                        ]
                                    ),
                                    dbc.Card(
                                        className="shadow-sm",
                                        style={
                                            'backgroundColor': 'white',
                                            'padding': '15px',
                                            'height': 'calc(50% - 0.5vh)',
                                            'display': 'flex',
                                            'flexDirection': 'column'
                                        },
                                        children=[
                                            html.H5("Trade Placeholder Worldmap", className="card-title mb-3"),
                                            dcc.Graph(
                                                id='tdb_scatter-graph',
                                                figure={},
                                                style={'flex': '1', 'minHeight': '250px'}
                                            )
                                        ]
                                    )
                                ],
                                style={
                                    'display': 'flex',
                                    'flexDirection': 'column',
                                    'justifyContent': 'space-between',
                                    'height': '100%'
                                }
                            ),
                            md=6, xs=12,
                            style={'display': 'flex', 'flexDirection': 'column', 'height': '100%'}
                        )
                    ],
                    className="flex-fill overflow-auto align-items-stretch",
                    style={'paddingBottom': '5px', 'marginBottom': '0', '--bs-gutter-x': '1vh'}
                ),

                # ==== NAVIGATION BUTTONS ====
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button("← Price Dashboard", color="info", href="/price",
                                       className="mt-1 mb-1 w-100"),
                            xs=6, sm=6, md=3
                        ),
                        dbc.Col(
                            dbc.Button("Validation Dashboard →", color="secondary", href="/validation",
                                       className="mt-1 mb-1 w-100"),
                            xs=6, sm=6, md=3, className="ms-auto"
                        )
                    ],
                    justify="between",
                    className="mt-auto mb-1"
                )
            ]
        )

        return app_layout

