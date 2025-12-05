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
import re
from Toolbox.parameters.default_parameters import default_plot_settings, printing_plot_settings

PACKAGEDIR = Path(__file__).parent.parent.absolute()


class ValidationDB:

    def __init__(self, app, data: pd.DataFrame = None, print_settings: bool = False):
        self.data = data
        self.app = app
        self.start = self.data['Year'].min()
        self.end = self.data['Year'].max()
        self.model_colors = self.get_colors()
        self.logo = PACKAGEDIR / 'timba_validation_logo.png'
        self.app_layout = self.create_layout()
        self.create_callbacks()
        if print_settings:
            self.plot_settings = printing_plot_settings
        else:
            self.plot_settings = default_plot_settings

    def get_colors(self):
        color_palette = px.colors.qualitative.Bold
        model_colors = {
            "TiMBA": tuple(map(int, re.findall(r'\d+', color_palette[1]))),
            "GLOBIOM": tuple(map(int, re.findall(r'\d+', color_palette[4]))),
            "GFPM": tuple(map(int, re.findall(r'\d+', color_palette[3]))),
            "GTM": tuple(map(int, re.findall(r'\d+', color_palette[2]))),
            "Max": tuple(map(int, re.findall(r'\d+', color_palette[6]))),
            "Min": tuple(map(int, re.findall(r'\d+', color_palette[8]))),
        }

        return model_colors

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
            style={'backgroundColor': 'white',
                   'height': 'calc(100vh - 80px)',  # Adapting to the hight of the navigation header
                   'display': 'flex',
                   'flexDirection': 'column',
                   'overflow': 'hidden'
                   },
            children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Card(className="border-0 shadow-sm",
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
                                                    dcc.Dropdown(id='vdb_region-dropdown',
                                                                 options=[{'label': i, 'value': i}
                                                                          for i in sorted(self.data['Region'].dropna().unique())],
                                                                 multi=True,
                                                                 placeholder='Select Region...',
                                                                 style=dropdown_style),
                                                    dcc.Dropdown(id='vdb_estimate-dropdown',
                                                                 options=[{'label': i, 'value': i}
                                                                          for i in sorted(self.data['Estimate'].dropna().unique())],
                                                                 placeholder='Select Estimate...',
                                                                 multi=True,
                                                                 style=dropdown_style),
                                                    dcc.Dropdown(id='vdb_scenario-dropdown',
                                                                 options=[{'label': 'All', 'value': 'All'}] +
                                                                         [{'label': i, 'value': i}
                                                                          for i in sorted(self.data['Scenario'].dropna().unique())],
                                                                 placeholder='Select Scenario...',
                                                                 multi=True,
                                                                 style=dropdown_style),
                                                    dcc.Dropdown(id='vdb_model-dropdown',
                                                                 options=[{'label': 'All', 'value': 'All'}] +
                                                                         [{'label': i, 'value': i}
                                                                          for i in sorted(self.data['Model'].dropna().unique())],
                                                                 placeholder='Select Model...',
                                                                 multi=True,
                                                                 style=dropdown_style),
                                                    # Download-Button
                                                    html.Button(
                                                        "⬇️ CSV Export",
                                                        id="vdb_btn_csv",
                                                        className="ml-auto btn btn-outline-secondary",
                                                        style={
                                                            'height': '38px',
                                                            'marginLeft': 'auto',
                                                            'padding': '0 15px',
                                                            'borderRadius': '4px',
                                                        }
                                                    ),
                                                    dcc.Download(id="vdb_download-dataframe-csv")
                                                 ])
                                         ])
                                 ])
                    ])
                ], className="mb-3"),
                # ==== MAIN CONTENT ====
                dbc.Row([
                    # Left column
                    dbc.Col(children=[
                        dbc.Card(className="h-100 shadow-sm",
                                 style={
                                     'backgroundColor': 'white',
                                     'padding': '15px',
                                     'display': 'flex',
                                     'flexDirection': 'column',
                                     'height': '100%'
                                 },
                                 children=[
                                     dbc.CardBody(
                                         style={
                                             "display": "flex",
                                             "flexDirection": "column",
                                             "height": "100%",
                                             "padding": "10px"
                                         },
                                         children=[
                                             # html.H5("Figure filter", className="card-title"),
                                             html.Div([dcc.Dropdown(
                                                 id='vdb_figure-type-dropdown',
                                                 options=[{'label': i, 'value': i}
                                                          for i in ['range', 'min_max', 'ssp_fsm_range', 'ssp_fsm_all']],
                                                 placeholder="Select Figure Type...",
                                                 value='ssp_fsm_range',
                                                 style=dropdown_style
                                             )], style={'marginBottom': '15px', 'flex': '0 0 auto'}),
                                             dcc.Graph(
                                                 id='vdb_formip-plot',
                                                 config={'toImageButtonOptions': {'format': 'png'},
                                                         'displayModeBar': True},
                                                 style={'flex': '1 1 auto',
                                                        'height': '100%',
                                                        'minHeight': '300px'
                                                        }
                                             )
                                         ])
                                 ])
                    ],
                        md=6, xs=12, className="mb-1",
                        style={'display': 'flex', 'flexDirection': 'column'}),
                    # Right column
                    dbc.Col(children=[
                        dbc.Card(className="h-100 shadow-sm",
                                 style={
                                     'backgroundColor': 'white',
                                     'padding': '15px',
                                     'display': 'flex',
                                     'flexDirection': 'column',
                                     'height': '100%'
                                 },
                                 children=[
                                     dbc.CardBody(style={
                                         "display": "flex",
                                         "flexDirection": "column",
                                         "height": "100%",
                                         "padding": "10px"
                                     }, children=[
                                         # html.H5("Figure filter", className="card-title"),
                                         html.Div([
                                             dcc.Dropdown(
                                                 id='vdb_value-type-dropdown',
                                                 options=[{'label': i, 'value': i} for i in ['relative values', 'absolute values']],
                                                 placeholder="Select Value Type...",
                                                 value='relative values',
                                                 style=dropdown_style
                                             )
                                         ], style={'marginBottom': '15px', 'flex': '0 0 auto'}),
                                         html.Div([
                                             dcc.Dropdown(
                                                 id='vdb_start-year-dropdown',
                                                 options=[{'label': i, 'value': i} for i in
                                                          sorted(self.data['Year'].dropna().unique())],
                                                 placeholder="Select Start Year ...",
                                                 value=2020,
                                                 style=dropdown_style
                                             )
                                         ], style={'marginBottom': '15px', 'flex': '0 0 auto'}),
                                         html.Div([
                                             dcc.Dropdown(
                                                 id='vdb_end-year-dropdown',
                                                 options=[{'label': i, 'value': i} for i in
                                                          sorted(self.data['Year'].dropna().unique())],
                                                 placeholder="Select End Year ...",
                                                 value=2100,
                                                 style=dropdown_style
                                             )
                                         ], style={'marginBottom': '15px', 'flex': '0 0 auto'}),
                                         dcc.Graph(
                                             id='vdb_formip-bar',
                                             config={'toImageButtonOptions': {'format': 'png'},
                                                     'displayModeBar': True},
                                             style={'flex': '1 1 auto',
                                                    'height': '100%',
                                                    'minHeight': '300px'
                                                    }
                                         )
                                     ])
                                 ])
                    ], md=6, xs=12, className="mb-1",
                        style={'display': 'flex', 'flexDirection': 'column'})
                ],
                    className="flex-fill overflow-auto align-items-stretch",
                    style={'paddingBottom': '5px', 'marginBottom': '0', '--bs-gutter-x': '1vh'}),
                # ==== NAVIGATION BUTTONS ====
                dbc.Row([
                    dbc.Col(
                        dbc.Button("← Trade Dashboard", color="warning", href="/trade",
                                   className="mt-1 mb-1 w-100"),
                        xs=6, sm=6, md=3
                    )
                ],
                    justify="between",
                    className="mt-auto mb-1"
                )
            ])

        return app_layout

    def create_callbacks(self):
        @self.app.callback([
            Output('vdb_formip-plot', 'figure'),
            Output('vdb_formip-bar', 'figure')],
            [
                Input('vdb_region-dropdown', 'value'),
                Input('vdb_estimate-dropdown', 'value'),
                Input('vdb_scenario-dropdown', 'value'),
                Input('vdb_model-dropdown', 'value'),
                Input('vdb_figure-type-dropdown', 'value'),
                Input('vdb_value-type-dropdown', 'value'),
                Input('vdb_start-year-dropdown', 'value'),
                Input('vdb_end-year-dropdown', 'value')]
        )
        def update_plots(region, estimate, scenario, model, figure_type, value_type, start_year, end_year):
            return self.update_plot_validation(region, estimate, scenario, model, figure_type, value_type, start_year,
                                               end_year)

        @self.app.callback(
            Output("vdb_download-dataframe-csv", "data"),
            Input("vdb_btn_csv", "n_clicks"),
            [State('vdb_region-dropdown', 'value'),
             State('vdb_estimate-dropdown', 'value'),
             State('vdb_scenario-dropdown', 'value'),
             State('vdb_model-dropdown', 'value')],
            prevent_initial_call=True
        )
        def func(n_clicks, region, estimate, scenario, model):
            if n_clicks is None:
                raise dash.exceptions.PreventUpdate

            filtered_data = self.filter_data(region, estimate, scenario, model)
            return dcc.send_data_frame(filtered_data.to_csv, "filtered_external_validation_data.csv", index=False)

    def filter_data(self, region, estimate, scenario, model):
        filtered_data = self.data.copy()
        if isinstance(region, list):
            if not region:
                filtered_data = filtered_data.iloc[0:0]
            else:
                filtered_data = filtered_data[filtered_data['Region'].isin(region)]
        if isinstance(model, list):
            if not model:
                filtered_data = filtered_data.iloc[0:0]
            elif "All" not in model:
                filtered_data = filtered_data[filtered_data['Model'].isin(model)]
        if isinstance(estimate, list):
            if not estimate:
                filtered_data = filtered_data.iloc[0:0]
            else:
                filtered_data = filtered_data[filtered_data['Estimate'].isin(estimate)]
        if isinstance(scenario, list):
            if not scenario:
                filtered_data = filtered_data.iloc[0:0]
            elif "All" not in scenario:
                filtered_data = filtered_data[filtered_data['Scenario'].isin(scenario)]
        return filtered_data

    def plot_min_max(self, data):
        fig_formip_main = go.Figure()

        for (model, region), subset in data.groupby(['Model', 'Region']):
            color = self.model_colors.get(model, (0, 0, 0))
            dash = 'solid'

            if model == 'Max':
                name_up_bnd = 'Upper bound max'
                name_low_bnd = 'Confidence interval max'
                name_mean = 'Mean max'
            if model == 'Min':
                name_up_bnd = 'Upper bound min'
                name_low_bnd = 'Confidence interval min'
                name_mean = 'Mean min'
            if model == 'TiMBA':
                name_up_bnd = 'Upper bound TiMBA'
                name_low_bnd = 'Confidence interval TiMBA'
                name_mean = 'Mean TiMBA'

            subset_new = pd.DataFrame()
            for year in subset['Year'].unique():
                subset_tmp = subset[subset['Year'] == year].reset_index(drop=True)
                subset_tmp_info = pd.DataFrame([subset_tmp.iloc[0, 0: -1]])
                subset_tmp_mean = pd.DataFrame([subset_tmp["Data"].mean()], columns=['mean'])
                subset_tmp_max = pd.DataFrame([subset_tmp["Data"].max()], columns=['max'])
                subset_tmp_min = pd.DataFrame([subset_tmp["Data"].min()], columns=['min'])

                subset_tmp_new = pd.concat(
                    [subset_tmp_info, subset_tmp_mean, subset_tmp_max, subset_tmp_min], axis=1).reset_index(drop=True)
                subset_new = pd.concat([subset_new, subset_tmp_new], axis=0)

            # Add upper bound
            fig_formip_main.add_trace(go.Scatter(
                x=subset_new['Year'],
                y=subset_new['max'],
                line=dict(color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)", width=0),
                mode='lines',
                showlegend=False,
                name=name_up_bnd
            ))

            # Add lower bound and fill to upper
            fig_formip_main.add_trace(go.Scatter(
                x=subset_new['Year'],
                y=subset_new['min'],
                fill='tonexty',
                fillcolor=f"rgba({color[0]}, {color[1]}, {color[2]}, 0.2)",
                line=dict(color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)", width=0),
                mode='lines',
                showlegend=True,
                name=name_low_bnd
            ))

            # Add the mean line
            fig_formip_main.add_trace(go.Scatter(
                x=subset_new['Year'],
                y=subset_new['mean'],
                line=dict(color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)", dash=dash),
                mode='lines',
                name=name_mean
            ))
        return fig_formip_main

    def plot_range(self, formip_data, timba_data):
        fig_formip_main = go.Figure()

        color_range = self.model_colors.get("", (0, 0, 0))
        dash = 'solid'
        formip_data = (formip_data.groupby('Year').agg(
            mean=('Data', 'mean'),
            min=('Data', 'min'),
            max=('Data', 'max')).reset_index())

        formip_data['lower_err'] = formip_data['mean'] - formip_data['min']
        formip_data['upper_err'] = formip_data['max'] - formip_data['mean']

        # Add upper bound ForMIP range
        fig_formip_main.add_trace(go.Scatter(
            x=formip_data['Year'],
            y=formip_data['max'],
            line=dict(color=f"rgba({color_range[0]}, {color_range[1]}, {color_range[2]}, 1)", width=0),
            mode='lines',
            showlegend=False,
            name="Upper bound"
        ))

        # Add lower bound ForMIP range
        fig_formip_main.add_trace(go.Scatter(
            x=formip_data['Year'],
            y=formip_data['min'],
            fill='tonexty',
            fillcolor=f"rgba({color_range[0]}, {color_range[1]}, {color_range[2]}, 0.2)",
            line=dict(color=f"rgba({color_range[0]}, {color_range[1]}, {color_range[2]}, 1)", width=0),
            mode='lines',
            showlegend=True,
            name="ForMIP Min-Max range"
        ))

        color = self.model_colors.get("TiMBA", (0, 0, 0))
        timba_data = (timba_data.groupby('Year').agg(
            mean=('Data', 'mean'),
            min=('Data', 'min'),
            max=('Data', 'max')).reset_index())

        timba_data['lower_err'] = timba_data['mean'] - timba_data['min']
        timba_data['upper_err'] = timba_data['max'] - timba_data['mean']

        # Add upper bound TiMBA
        fig_formip_main.add_trace(go.Scatter(
            x=timba_data['Year'],
            y=timba_data['max'],
            line=dict(color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)", width=0),
            mode='lines',
            showlegend=False,
            name="Upper bound"
        ))

        # Add lower bound TiMBA
        fig_formip_main.add_trace(go.Scatter(
            x=timba_data['Year'],
            y=timba_data['min'],
            fill='tonexty',
            fillcolor=f"rgba({color[0]}, {color[1]}, {color[2]}, 0.2)",
            line=dict(color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)", width=0),
            mode='lines',
            showlegend=True,
            name="TiMBA Min-Max range"
        ))

        # Add the mean line TiMBA
        fig_formip_main.add_trace(go.Scatter(
            x=timba_data['Year'],
            y=timba_data['mean'],
            line=dict(color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)", dash=dash),
            mode='lines',
            name="TiMBA mean"
        ))
        return fig_formip_main

    def plot_ssp_fsm_range(self, data):
        fig_formip_main = go.Figure()

        for (model, region), subset in data.groupby(['Model', 'Region']):
            color = self.model_colors.get(model, (0, 0, 0))
            dash = 'solid'

            name_up_bnd = f'Upper bound {model}'
            name_low_bnd = f'Min-Max range {model}'
            name_mean = f'Mean {model}'

            subset_new = pd.DataFrame()
            for year in subset['Year'].unique():
                subset_tmp = subset[subset['Year'] == year].reset_index(drop=True)
                subset_tmp_info = pd.DataFrame([subset_tmp.iloc[0, 0: -1]])
                subset_tmp_mean = pd.DataFrame([subset_tmp["Data"].mean()], columns=['mean'])
                subset_tmp_max = pd.DataFrame([subset_tmp["Data"].max()], columns=['max'])
                subset_tmp_min = pd.DataFrame([subset_tmp["Data"].min()], columns=['min'])

                subset_tmp_new = pd.concat(
                    [subset_tmp_info, subset_tmp_mean, subset_tmp_max, subset_tmp_min], axis=1).reset_index(drop=True)
                subset_new = pd.concat([subset_new, subset_tmp_new], axis=0)

            # Add upper bound
            fig_formip_main.add_trace(go.Scatter(
                x=subset_new['Year'],
                y=subset_new['max'],
                line=dict(color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)", width=0),
                mode='lines',
                showlegend=False,
                name=name_up_bnd
            ))

            # Add lower bound and fill to upper
            fig_formip_main.add_trace(go.Scatter(
                x=subset_new['Year'],
                y=subset_new['min'],
                fill='tonexty',
                fillcolor=f"rgba({color[0]}, {color[1]}, {color[2]}, 0.2)",
                line=dict(color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)", width=0),
                mode='lines',
                showlegend=True,
                name=name_low_bnd
            ))

            # Add the mean line
            fig_formip_main.add_trace(go.Scatter(
                x=subset_new['Year'],
                y=subset_new['mean'],
                line=dict(color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)", dash=dash),
                mode='lines',
                name=name_mean
            ))
        return fig_formip_main

    def plot_ssp_fsm_all(self, data):
        fig_formip_main = go.Figure()
        dash_styles = {}
        dash_list = ["solid", "dash", "dot", "longdash", "dashdot", "longdashdot"]
        dash_runner = 0
        for scenario in data["Scenario"].unique():
            if dash_runner > 5:
                dash_runner = 0

            dash_styles[scenario] = dash_list[dash_runner]

            dash_runner += 1

        for (model, region, scenario), subset in data.groupby(['Model', 'Region', 'Scenario']):
            color = self.model_colors.get(model, (0, 0, 0))
            name_mean = f'{model}_{scenario}'

            subset_new = pd.DataFrame()
            for year in subset['Year'].unique():
                subset_tmp = subset[subset['Year'] == year].reset_index(drop=True)
                subset_tmp_info = pd.DataFrame([subset_tmp.iloc[0, 0: -1]])
                subset_tmp_mean = pd.DataFrame([subset_tmp["Data"].mean()], columns=['mean'])

                subset_tmp_new = pd.concat(
                    [subset_tmp_info, subset_tmp_mean], axis=1).reset_index(drop=True)
                subset_new = pd.concat([subset_new, subset_tmp_new], axis=0)

            # Add the mean line
            fig_formip_main.add_trace(go.Scatter(
                x=subset_new['Year'],
                y=subset_new['mean'],
                line=dict(color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)", dash=dash_styles[scenario]),
                mode='lines',
                name=name_mean
            ))

        return fig_formip_main

    def bar_plot_fsm(self, data, value_type, start_year, end_year):
        fig_formip_second = go.Figure()

        data_grouped = data.groupby(['Model', 'Region'])

        for (model, region), subset in data_grouped:
            color = self.model_colors.get(model, (0, 0, 0))
            scenario_diffs = []

            for scenario in subset['Scenario'].unique():
                scenario_data = subset[subset['Scenario'] == scenario]

                try:
                    data_start_year = float(scenario_data[scenario_data['Year'] == start_year]['Data'])
                    data_end_year = float(scenario_data[scenario_data['Year'] == end_year]['Data'])

                    if value_type == 'absolute values':
                        data_diff = data_end_year - data_start_year
                    elif value_type == 'relative values':
                        data_diff = (data_end_year - data_start_year) / data_end_year * 100

                    scenario_diffs.append(data_diff)
                except Exception:
                    continue

            if len(scenario_diffs) == 0:
                continue  # No valid data

            mean_diff = np.mean(scenario_diffs)
            min_diff = np.min(scenario_diffs)
            max_diff = np.max(scenario_diffs)

            error_plus = max_diff - mean_diff
            error_minus = mean_diff - min_diff

            fig_formip_second.add_trace(go.Bar(
                x=[f'{model}<br>{start_year} - {end_year}'],
                y=[mean_diff],
                name=model,
                marker_color=f"rgba({color[0]}, {color[1]}, {color[2]}, 0.6)",
                error_y=dict(
                    type='data',
                    symmetric=False,
                    array=[error_plus],  # Upper CI
                    arrayminus=[error_minus],  # Lower CI
                    thickness=1.5,
                    width=5,
                    color=f"rgba({color[0]}, {color[1]}, {color[2]}, 1)"
                )
            ))

        return fig_formip_second

    def update_plot_validation(self, region, estimate, scenario, model, figure_type, value_type, start_year, end_year):
        graphic_template = 'plotly_white'  # 'plotly_dark'#'plotly_white'
        filtered_data = self.filter_data(region, estimate, scenario, model)

        filtered_data = filtered_data.reset_index(drop=True)
        filtered_data['Model'] = filtered_data['Model'].str.strip()

        # ForMIP main plot (absolute value comparison)

        if (figure_type == 'min_max') | (figure_type == 'range'):
            timba_data = filtered_data[filtered_data['Model'] == 'TiMBA'].reset_index(drop=True)

            fsm_data = filtered_data[filtered_data['Model'] != 'TiMBA'].reset_index(drop=True)
            fsm_data_max = fsm_data.groupby(['Year', 'Region', 'Estimate', 'Scenario'])['Data'].max().reset_index()
            fsm_data_min = fsm_data.groupby(['Year', 'Region', 'Estimate', 'Scenario'])['Data'].min().reset_index()
            fsm_data_max['Model'] = 'Max'
            fsm_data_min['Model'] = 'Min'

            if figure_type == 'min_max':
                data_fin = pd.concat([timba_data, fsm_data_max, fsm_data_min], axis=0).reset_index(drop=True)
                fig_formip_main = self.plot_min_max(data=data_fin)

            else:
                data_fin = pd.concat([fsm_data_max, fsm_data_min], axis=0).reset_index(drop=True)
                fig_formip_main = self.plot_range(formip_data=data_fin, timba_data=timba_data)

        elif figure_type == "ssp_fsm_range":
            fig_formip_main = self.plot_ssp_fsm_range(data=filtered_data)

        elif figure_type == "ssp_fsm_all":
            fig_formip_main = self.plot_ssp_fsm_all(data=filtered_data)

        else:
            fig_formip_main = go.Figure()

        title_formip_main = self.generate_title(
            region=region, estimate=estimate, scenario=scenario, model=model, plot="plot", value_type=value_type)

        fig_formip_main.update_layout(
            title='<br>'.join(textwrap.wrap(title_formip_main, width=150)),
            xaxis_title='Year',
            # yaxis_title=f'{estimate[0]}',
            xaxis=dict(gridcolor='white'),
            yaxis=dict(rangemode='nonnegative', zeroline=True, zerolinewidth=2, zerolinecolor='LightGrey',
                       gridcolor='white'),
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
            margin=dict(l=35, r=35, t=110, b=90),
            hovermode='x unified',
            template=graphic_template,
            plot_bgcolor='rgb(229, 236, 246)'
        )

        # ForMIP secondary plot (relative value comparison)
        fig_formip_second = self.bar_plot_fsm(data=filtered_data,
                                              value_type=value_type,
                                              start_year=start_year,
                                              end_year=end_year)

        title_formip_second = self.generate_title(
            region=region, estimate=estimate, scenario=scenario, model=model, plot="bar_plot", value_type=value_type)
        if value_type == "absolute values":
            pass  # yaxis_title = f'Difference in {estimate[0]}'
        if value_type == "relative values":
            pass  # yaxis_title = f'Difference in {' '.join(estimate[0].split(' ')[:-1])} (%)'

        fig_formip_second.update_layout(
            title='<br>'.join(textwrap.wrap(title_formip_second, width=150)),
            # yaxis_title=yaxis_title,
            xaxis=dict(gridcolor='white'),
            yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='LightGrey', gridcolor='white'),
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
            margin=dict(l=35, r=35, t=135, b=100),
            hovermode='x unified',
            template=graphic_template,
            plot_bgcolor='rgb(229, 236, 246)'
        )

        return fig_formip_main, fig_formip_second

    def generate_title(self, region, estimate, scenario, model, plot, value_type):
        title_parts = []
        if plot == "bar_plot":
            if value_type == "absolute values":
                pass  # title_parts.append(f'Difference in {estimate[0]}')
            if value_type == "relative values":
                pass  # title_parts.append(f'Difference in {' '.join(estimate[0].split(' ')[:-1])} (%)')
        else:
            title_parts.append(f"{estimate}")
        if region:
            title_parts.append(f" for {region}<br>")
        if scenario:
            title_parts.append(f"Scenarios: {scenario}<br>")
        if model:
            title_parts.append(f"Models: {model}")
        title = "".join(title_parts) if title_parts else "all data"
        clean_title = title.replace("'", "").replace("[", "").replace("]", "")
        return clean_title
