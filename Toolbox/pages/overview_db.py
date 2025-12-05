import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import textwrap
from Toolbox.parameters.default_parameters import default_plot_settings, printing_plot_settings


PACKAGEDIR = Path(__file__).parent.parent.absolute()


class OverviewDB:
    def __init__(self, app, data, print_settings: bool = False, color_list: list = None):
        self.data = data
        self.app = app
        self.start = self.data['year'].min()
        self.end = self.data['year'].max()
        self.color_list = color_list
        self.app_layout = self.create_layout()
        self.create_callbacks()
        if print_settings:
            self.plot_settings = printing_plot_settings
        else:
            self.plot_settings = default_plot_settings

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
                dbc.Row([
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
                                                options=[{'label': i, 'value': i} for i in
                                                         sorted(self.data['ISO3'].dropna().unique())],
                                                multi=True,
                                                placeholder="Select Country...",
                                                style=dropdown_style
                                            ),

                                            dcc.Dropdown(
                                                id='odb_continent-dropdown',
                                                options=[{'label': i, 'value': i} for i in
                                                         sorted(self.data['Continent'].dropna().unique())],
                                                multi=True,
                                                placeholder="Select Continent...",
                                                style=dropdown_style
                                            ),

                                            dcc.Dropdown(
                                                id='odb_domain-dropdown',
                                                options=[{'label': i, 'value': i} for i in
                                                         sorted(self.data['domain'].dropna().unique())],
                                                multi=True,
                                                placeholder="Select Domain...",
                                                style=dropdown_style
                                            ),

                                            dcc.Dropdown(
                                                id='odb_commodity-dropdown',
                                                options=[{'label': i, 'value': i} for i in
                                                         sorted(self.data['Commodity'].dropna().unique())],
                                                multi=True,
                                                placeholder="Select Commodity...",
                                                style=dropdown_style
                                            ),

                                            dcc.Dropdown(
                                                id='odb_commodity-group-dropdown',
                                                options=[{'label': i, 'value': i} for i in
                                                         self.data['Commodity_Group'].dropna().unique().tolist()],
                                                multi=True,
                                                placeholder="Select Commodity Group...",
                                                style=dropdown_style
                                            ),

                                            dcc.Dropdown(
                                                id='odb_scenario-filter',
                                                options=[{'label': i, 'value': i}
                                                         for i in self.data['Scenario'].unique()],
                                                multi=True,
                                                placeholder="Select Scenario...",
                                                style=dropdown_style
                                            ),

                                            html.Button("⬇️ CSV Export",
                                                        id="odb_btn_csv",
                                                        className="ml-auto btn btn-outline-secondary",
                                                        style={
                                                            'borderRadius': '4px',
                                                        }
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
                        style={'height': '100%',
                               'display': 'flex',
                               'flexDirection': 'column'}
                    ),
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
                                    # === FOREST PLOT and WORLD MAP CARD ===
                                    dbc.Col(
                                        [
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
                    )
                ], style={"height": "calc(100% - 6.5vh)"}),
                # ==== NAVIGATION BUTTONS ====
                dbc.Row(
                    [
                        dbc.Col([""]),
                        dbc.Col(
                            dbc.Button("Forest Dashboard →", color="success", href="/forest",
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

    def create_callbacks(self):
        @self.app.callback(
            [Output('odb_quantity-plot', 'figure'),
             Output('odb_price-plot', 'figure'),
             Output('odb_forstock-plot', 'figure')],
            [Input('odb_region-dropdown', 'value'),
             Input('odb_continent-dropdown', 'value'),
             Input('odb_domain-dropdown', 'value'),
             Input('odb_commodity-dropdown', 'value'),
             Input('odb_commodity-group-dropdown', 'value'),
             Input('odb_scenario-filter', 'value')]
        )
        def update_plots(region, continent, domain, commodity, commodity_group, scenario):
            return self.update_plot_data(region, continent, domain, commodity, commodity_group, scenario)

        @self.app.callback(
            Output('odb_world-map', 'figure'),
            [Input('odb_scenario-filter', 'value'),
             Input('odb_year-filter', 'value'),
             Input('odb_region-dropdown', 'value'),
             Input('odb_continent-dropdown', 'value'),
             Input('odb_domain-dropdown', 'value'),
             Input('odb_commodity-dropdown', 'value'),
             Input('odb_commodity-group-dropdown', 'value')]
        )
        def update_world_map(scenario, year, region, continent, domain, commodity, commodity_group):
            return self.create_world_map(region, continent, domain, commodity, commodity_group, scenario, year)

        @self.app.callback(
            Output("odb_download-dataframe-csv", "data"),
            Input("odb_btn_csv", "n_clicks"),
            [State('odb_region-dropdown', 'value'),
             State('odb_continent-dropdown', 'value'),
             State('odb_domain-dropdown', 'value'),
             State('odb_commodity-dropdown', 'value'),
             State('odb_commodity-group-dropdown', 'value'),
             State('odb_scenario-filter', 'value')],  # Geändert von Input zu State
            prevent_initial_call=True
        )
        def func(n_clicks, region, continent, domain, commodity, commodity_group, scenario):
            if n_clicks is None:
                raise dash.exceptions.PreventUpdate
            filtered_data = self.filter_data(region, continent, domain, commodity, commodity_group, scenario)
            return dcc.send_data_frame(filtered_data.to_csv, "filtered_data.csv")

    def filter_data(self, region, continent, domain, commodity, commodity_group, scenario):
        filtered_data = self.data
        if region and isinstance(region, list):
            filtered_data = filtered_data[filtered_data['ISO3'].isin(region)]
        if continent and isinstance(continent, list):
            filtered_data = filtered_data[filtered_data['Continent'].isin(continent)]
        if domain and isinstance(domain, list):
            filtered_data = filtered_data[filtered_data['domain'].isin(domain)]
        if commodity and isinstance(commodity, list):
            filtered_data = filtered_data[filtered_data['Commodity'].isin(commodity)]
        if commodity_group and isinstance(commodity_group, list):
            filtered_data = filtered_data[filtered_data['Commodity_Group'].isin(commodity_group)]
        if scenario and isinstance(scenario, list):
            filtered_data = filtered_data[filtered_data['Scenario'].isin(scenario)]
        filtered_data = self.remove_extreme_outliers(df=filtered_data, col='price')
        return filtered_data

    def update_plot_data(self, region, continent, domain, commodity, commodity_group, scenario):
        graphic_template = 'plotly_white'  # 'plotly_dark'#'plotly_white'
        filtered_data = self.filter_data(region, continent, domain, commodity, commodity_group, scenario)

        # Quantity plot
        max_year = filtered_data['year'].max()
        grouped_data_quantity = filtered_data.groupby(['year', 'Scenario']).sum().reset_index()
        grouped_data_quantity = grouped_data_quantity[
            (grouped_data_quantity["year"] >= self.start) & (grouped_data_quantity["year"] <= self.end)]
        fig_quantity = go.Figure()
        for i, scenario in enumerate(grouped_data_quantity['Scenario'].unique()):
            subset = grouped_data_quantity[grouped_data_quantity['Scenario'] == scenario]
            color = self.color_list[i % len(self.color_list)]
            dash = 'solid' if scenario in ['Historic Data'] else 'dash'
            fig_quantity.add_trace(go.Scatter(x=subset['year'], y=subset['quantity'] * 1000, mode='lines',
                                              name=f'{scenario}', line=dict(color=color, dash=dash,
                                                                            width=self.plot_settings["line_witdh"])))
        title_quantity = self.generate_title(region, continent, domain, commodity, commodity_group)
        title = "Quantity by Year and Scenario for " + title_quantity
        fig_quantity.update_layout(
            title=dict(text='<br>'.join(textwrap.wrap(title, width=90)),
                       font=dict(size=self.plot_settings["title_font_size"])),
            xaxis_title='Year',
            yaxis_title='Quantity',
            xaxis=dict(range=[2015.5, max_year],
                       title=dict(text='Year', font=dict(size=self.plot_settings["font_size"])),
                       tickfont=dict(size=self.plot_settings["tick_font_size"])),
            yaxis=dict(rangemode='nonnegative', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey',
                       title=dict(text='Quantity',
                                  font=dict(size=self.plot_settings["font_size"])),
                       tickfont=dict(size=self.plot_settings["tick_font_size"])),
            legend_title='Scenario',
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5,
                        font=dict(size=self.plot_settings["legend_font_size"])),
            margin=dict(l=35, r=35, t=60, b=90),
            hovermode='x unified',
            template=graphic_template
        )

        # Price plot
        grouped_data_price = filtered_data.groupby(['year', 'Scenario']).mean().reset_index()
        max_year = grouped_data_price['year'].max() + 0.5

        fig_price = go.Figure()
        for i, scenario in enumerate(grouped_data_price['Scenario'].unique()):
            subset = grouped_data_price[grouped_data_price['Scenario'] == scenario]
            color = self.color_list[i % len(self.color_list)]
            fig_price.add_trace(go.Bar(x=subset['price'], y=subset['year'], orientation='h',
                                       name=f'{scenario}', marker_color=color))

        title_price = f'Price by Period and Scenario'
        fig_price.update_layout(
            title=title_price,
            xaxis_title='Price',
            yaxis_title='Year',
            yaxis=dict(range=[2020 - 0.5, max_year]),
            legend_title='Scenario',
            template=graphic_template,
            showlegend=False,
            # legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
            margin=dict(l=35, r=60, t=50, b=5),
            barmode='group'
        )

        # ForStock plot
        grouped_data_stock = filtered_data.drop(
            columns=['domain', 'price', 'quantity', 'CommodityCode', 'Commodity', 'Commodity_Group'])
        grouped_data_stock = grouped_data_stock.drop_duplicates().reset_index(drop=True)
        grouped_data_stock = grouped_data_stock.groupby(['year', 'Scenario']).agg({
            'ForStock': 'sum',
        }).reset_index()
        grouped_data_stock = grouped_data_stock[grouped_data_stock.Scenario != 'Historic Data']
        fig_stock = go.Figure()
        for i, scenario in enumerate(grouped_data_stock['Scenario'].unique()):
            subset = grouped_data_stock[grouped_data_stock['Scenario'] == scenario]
            color = self.color_list[i + 1 % len(self.color_list)]
            fig_stock.add_trace(go.Bar(x=subset['year'], y=subset['ForStock'],
                                       name=f'{scenario}', marker_color=color))

        min_year = 2020 - 1
        max_year = grouped_data_stock['year'].max() + 0.5

        min_val = grouped_data_stock['ForStock'].min() * 0.9
        max_val = grouped_data_stock['ForStock'].max() * 1.1

        fig_stock.update_layout(
            title='Forest Stock by Year and Scenario',
            xaxis_title='Year',
            xaxis=dict(range=[min_year, max_year]),
            yaxis=dict(range=[min_val, max_val]),
            yaxis_title='ForStock',
            template=graphic_template,
            showlegend=False,
            # legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5),
            margin=dict(l=50, r=50, t=40, b=5),
            barmode='group'
        )

        return fig_quantity, fig_price, fig_stock

    def generate_title(self, region, continent, domain, commodity, commodity_group):
        title_parts = []
        if region:
            title_parts.append(f"{region}")
        if continent:
            title_parts.append(f"{continent}")
        if domain:
            title_parts.append(f"{domain}")
        if commodity:
            title_parts.append(f"{commodity}")
        if commodity_group:
            title_parts.append(f"{commodity_group}")
        title = ", ".join(title_parts) if title_parts else "all data"
        clean_title = title.replace("'", "").replace("[", "").replace("]", "")
        return clean_title

    def create_world_map(self, region, continent, domain, commodity, commodity_group, scenario=None, year=None):
        filtered_data = self.filter_data(region, continent, domain, commodity, commodity_group, scenario)
        if year:
            filtered_data = filtered_data[filtered_data['year'] == year]
        country_data = filtered_data.groupby('ISO3')['quantity'].sum().reset_index()
        country_data = country_data[country_data['quantity'] >= 0.001].reset_index()

        fig = px.choropleth(
            country_data,
            locations="ISO3",
            color="quantity",
            hover_name="ISO3",
            color_continuous_scale="Greens"
        )

        title = 'Worldmap for ' + self.generate_title(region, continent, domain, commodity, commodity_group)
        fig.update_layout(
            # title= '<br>'.join(textwrap.wrap(title, width=43)),
            geo=dict(
                showcoastlines=True,
                coastlinecolor="LightGray",
                showocean=False,
                oceancolor="LightBlue",
                projection_type='natural earth',
                # Grenzen bestimmen
                lonaxis_range=[-360, 360],  # Längengradbereich
                lataxis_range=[-55, 55],  # Breitengradbereich
            ),
            margin=dict(l=1, r=1, t=1, b=1),  # Ränder minimieren
            coloraxis_showscale=False  # Legende entfernen
        )

        return fig

    def get_last_historic_year(self):
        historic_data = self.data[self.data['Scenario'] == 'Historic Data']
        if not historic_data.empty:
            return historic_data['year'].max()
        else:
            return self.data['year'].max()

    def remove_extreme_outliers(self, df: pd.DataFrame, col: str, threshhold: float = 50):
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outlier_threshold = threshhold * IQR
        df.loc[df[col] >= outlier_threshold, col] = np.nan
        return df
