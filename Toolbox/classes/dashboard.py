import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import webbrowser
from threading import Timer
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import textwrap
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

PACKAGEDIR = Path(__file__).parent.parent.absolute()

class DashboardPlotter:

    def __init__(self, data):
        self.data = data
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.start = self.data['year'].min()
        self.end = self.data['year'].max()
        self.color_list = self.generate_color_palette()
        self.logo = PACKAGEDIR/'timba_dashboard_logo.png'#'timba_logo_v3.png' 
        self.create_layout()
        self.create_callbacks()

    def create_layout(self):
        dropdown_style = {'height': '30px','marginBottom': '10px'}
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col(width=5),  # Leere Spalte für den linken Rand
                dbc.Col(
                    html.Img(src=self.app.get_asset_url('timba_dashboard_logo.png'), style={'height': '90px', 'width': 'auto'}),
                    width=1
                ),
                dbc.Col(
                    #html.H1("TiMBA Dashboard", className="text-center mb-4"), width=10
                )
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Filters", className="card-title"),
                            dcc.Dropdown(id='region-dropdown',
                                         options=[{'label': i, 'value': i} for i in sorted(self.data['ISO3'].dropna().unique())],
                                         multi=True,
                                         placeholder="Select Country...",
                                         style=dropdown_style),
                            dcc.Dropdown(id='continent-dropdown',
                                         options=[{'label': i, 'value': i} for i in sorted(self.data['Continent'].dropna().unique())],
                                         placeholder="Select Continent...",
                                         multi=True,
                                         style=dropdown_style),
                            dcc.Dropdown(id='domain-dropdown',
                                         options=[{'label': i, 'value': i} for i in sorted(self.data['domain'].dropna().unique())],
                                         placeholder="Select Domain...",
                                         multi=True,
                                         style=dropdown_style),
                            dcc.Dropdown(id='commodity-dropdown',
                                         options=[{'label': i, 'value': i} for i in sorted(self.data['Commodity'].dropna().unique())],
                                         placeholder="Select Commodity...",
                                         multi=True,
                                         style=dropdown_style),
                            dcc.Dropdown(id='commodity-group-dropdown',
                                         options=[{'label': i, 'value': i} for i in self.data['Commodity_Group'].dropna().unique().tolist()],
                                         placeholder="Select Commodity Group...",
                                         multi=True,
                                         style=dropdown_style),
                            dcc.Dropdown(id='scenario-filter',
                                         options=[{'label': i, 'value': i} for i in self.data['Scenario'].unique()],
                                         placeholder="Select Scenario...",
                                         multi=True,
                                         style=dropdown_style),
                            html.Button("Download CSV", id="btn_csv"),
                            dcc.Download(id="download-dataframe-csv"),
                        ])
                    ], className="mb-4", style={'white': 'white'}),  #filter box
                    dbc.Card([
                        dbc.CardBody([
                                dcc.Graph(id='price-plot',
                                      config={'toImageButtonOptions': {'format': 'png', 'filename': 'price_plot'}},
                                      style={'height': '45vh','width':'46vh'})
                    ])
                ], style={'white': 'white'})  #price box
            ], width=3),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(id='quantity-plot',
                                          config={'toImageButtonOptions': {'format': 'png', 'filename': 'quantity_plot'}},
                                          style={'height': '84.5vh'})
                            ])
                        ], style={'backgroundColor': 'white'}) #mittelbox
                    ], width=8), # Breite auf 8 reduziert
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(id='forstock-plot',  # Geändert: ID auf 'forstock-plot'
                                          config={'toImageButtonOptions': {'format': 'png'}},
                                          style={'height': '39vh'})
                            ])
                        ], style={'backgroundColor': 'white', 'marginBottom': '20px'}), # Abstand hinzugefügt
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Filter for Worldmap", className="card-title"),
                                #html.H6("Scenario Filter", className="card-title"),  # Titel für den Scenario-Filter
                                #html.H6("Year Filter", className="card-title"),  # Titel für den Year-Filter
                                dcc.Dropdown(
                                    id='year-filter',
                                    options=[{'label': i, 'value': i} for i in sorted(self.data['year'].unique())],
                                    placeholder="Select Year...",
                                    style=dropdown_style
                                ),
                                 dcc.Graph(id='world-map',  # Geändert: ID auf 'world-map'
                                          config={'toImageButtonOptions': {'format': 'png'}},
                                          style={'height': '32vh'})
                            ])
                        ], style={'backgroundColor': 'white'})
                    ], width=4), # Breite auf 4 gesetzt
                ]),
            ], width=9)
        ])
    ], fluid=True, style={'backgroundColor': 'white'}) #gesamthintergrund

    def create_callbacks(self):
        @self.app.callback(
            [Output('quantity-plot', 'figure'),
             Output('price-plot', 'figure'),
             Output('forstock-plot', 'figure')],
            [Input('region-dropdown', 'value'),
             Input('continent-dropdown', 'value'),
             Input('domain-dropdown', 'value'),
             Input('commodity-dropdown', 'value'),
             Input('commodity-group-dropdown', 'value'),
             Input('scenario-filter', 'value')]
        )
        def update_plots(region, continent, domain, commodity, commodity_group,scenario):
            return self.update_plot_data(region, continent, domain, commodity, commodity_group,scenario)

        @self.app.callback(
            Output('world-map', 'figure'),
            [Input('scenario-filter', 'value'),
             Input('year-filter', 'value'),
             Input('region-dropdown', 'value'),
             Input('continent-dropdown', 'value'),
             Input('domain-dropdown', 'value'),
             Input('commodity-dropdown', 'value'),
             Input('commodity-group-dropdown', 'value')]
        )
        def update_world_map(scenario, year, region, continent, domain, commodity, commodity_group):
            return self.create_world_map(region, continent, domain, commodity, commodity_group, scenario, year)

        @self.app.callback(
            Output("download-dataframe-csv", "data"),
            Input("btn_csv", "n_clicks"),
            [State('region-dropdown', 'value'),
            State('continent-dropdown', 'value'),
            State('domain-dropdown', 'value'),
            State('commodity-dropdown', 'value'),
            State('commodity-group-dropdown', 'value'),
            State('scenario-filter', 'value')],  # Geändert von Input zu State
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
        graphic_template='plotly_white'#'plotly_dark'#'plotly_white'
        filtered_data = self.filter_data(region, continent, domain, commodity, commodity_group, scenario)

        # Quantity plot
        grouped_data_quantity = filtered_data.groupby(['year', 'Scenario']).sum().reset_index()
        grouped_data_quantity = grouped_data_quantity[(grouped_data_quantity["year"] >= self.start) & (grouped_data_quantity["year"] < self.end)]
        fig_quantity = go.Figure()
        for i, scenario in enumerate(grouped_data_quantity['Scenario'].unique()):
            subset = grouped_data_quantity[grouped_data_quantity['Scenario'] == scenario]
            color = self.color_list[i % len(self.color_list)]
            dash = 'solid' if scenario in ['Historic Data'] else 'dash'
            fig_quantity.add_trace(go.Scatter(x=subset['year'], y=subset['quantity'], mode='lines',
                                              name=f'{scenario}', line=dict(color=color, dash=dash)))
        title_quantity = self.generate_title(region, continent, domain, commodity, commodity_group)
        title= "Quantity by Period and Scenario for " + title_quantity
        fig_quantity.update_layout(
            title='<br>'.join(textwrap.wrap(title, width=90)),
            xaxis_title='Year',
            yaxis_title='Quantity',
            yaxis=dict(rangemode='nonnegative', zeroline=True, zerolinewidth=2, zerolinecolor='LightGrey'),
            legend_title='Scenario',
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
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
            yaxis=dict(range=[2020-0.5, max_year]),
            legend_title='Scenario',
            template=graphic_template,
            showlegend=False,
            #legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
            margin=dict(l=35, r=60, t=50, b=5),
            barmode='group'
        )

        # ForStock plot
        grouped_data_stock = filtered_data.drop(columns=['domain', 'price','quantity','CommodityCode','Commodity','Commodity_Group'])
        grouped_data_stock = grouped_data_stock.drop_duplicates().reset_index(drop=True)
        grouped_data_stock = grouped_data_stock.groupby(['year', 'Scenario']).agg({
            'ForStock': 'sum',
            }).reset_index()
        grouped_data_stock = grouped_data_stock[grouped_data_stock.Scenario!='Historic Data']
        fig_stock = go.Figure()
        for i, scenario in enumerate(grouped_data_stock['Scenario'].unique()):
            subset = grouped_data_stock[grouped_data_stock['Scenario'] == scenario]
            color = self.color_list[i+1 % len(self.color_list)]
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
            #legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5),
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
            filtered_data = filtered_data[filtered_data['year']==year]
        country_data = filtered_data.groupby('ISO3')['quantity'].sum().reset_index()
        country_data = country_data[country_data['quantity']>=0.001].reset_index()

        fig = px.choropleth(
            country_data,
            locations="ISO3",
            color="quantity",
            hover_name="ISO3",
            color_continuous_scale="Greens"
        )

        title = 'Worldmap for '+ self.generate_title(region, continent, domain, commodity, commodity_group)
        fig.update_layout(
            #title= '<br>'.join(textwrap.wrap(title, width=43)),
            geo=dict(
                showcoastlines=True,
                coastlinecolor="LightGray",
                showocean=False,
                oceancolor="LightBlue",
                projection_type='natural earth',
                # Grenzen bestimmen
                lonaxis_range=[-360, 360],  # Längengradbereich
                lataxis_range=[-55, 55],   # Breitengradbereich
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
    
    def remove_extreme_outliers(self,df:pd.DataFrame,col:str,threshhold:float=50):        
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outlier_threshold = threshhold * IQR
        df.loc[df[col] >= outlier_threshold, col] = np.nan
        return df

    def generate_color_palette(self):
        """
        Generates a color palette depending on the scenario number in hex format
        :return: list of colors in hex format
        """
        sc_num = len(self.data['Scenario'].unique())
        color_palette = plt.get_cmap('Spectral')(np.linspace(0, 1, sc_num))
        hex_color_palette = [mcolors.to_hex(x) for x in color_palette]
        return hex_color_palette

    
    def open_browser(self):
        webbrowser.open_new("http://localhost:8050")


    def run(self):
        Timer(1, self.open_browser).start()
        self.app.run(host='localhost', debug=False, dev_tools_ui=False, dev_tools_hot_reload=False, port=8050)
