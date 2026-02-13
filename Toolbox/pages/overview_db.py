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

                        self._graph_card("odb_price_plot"),
                        html.Div(
                            self._graph_card("odb_main_plot"),
                            style={
                                "gridColumn": "2",
                                "gridRow": "1 / span 2",
                                "height": "100%", 
                                "minHeight": "0",  
                            }
                        ),#self._graph_card("odb_main_plot"),
                        html.Div(),
                        self._graph_card("odb_q_net_export_fig"),
                        html.Div(),
                        html.Div(),

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

                dcc.Download(id="tdb_download")
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
            Output("odb_main_plot", "figure"),
            Output("odb_price_plot", "figure"),
            Output("odb_q_net_export_fig", "figure"),
            Input("odb_continent-dropdown", "value"),
            Input("odb_country-dropdown", "value"),
            Input("odb_domain-dropdown", "value"),
            Input("odb_commodity-dropdown", "value"),
            Input("odb_commodity-group-dropdown", "value"),
            Input("odb_scenario-dropdown", "value"),
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
            main_plot = self.plots.create_quantity_plot(df)
            price_plot = self.plots.create_price_growth_plot(df=df)
            # q_export_fig = self.plots.create_trade_line_plot(df,"Export","quantity")
            q_net_export_fig = self.plots.create_trade_bar_plot(df,"Net Exports","quantity")
            # v_import_fig = self.plots.create_trade_line_plot(df,"Import","Value")
            # v_export_fig = self.plots.create_trade_line_plot(df,"Export","Value")
            # v_net_export_fig = self.plots.create_trade_bar_plot(df,"Net Exports","Value")

            return main_plot,price_plot,q_net_export_fig

        # ---------------------------
        # Download CSV
        # ---------------------------
        @self.app.callback(
            Output("odb_download", "data"),
            Input("odb_download-btn", "n_clicks"),
            State("odb_continent-dropdown", "value"),
            State("odb_country-dropdown", "value"),
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

    # def create_callbacks(self):
    #     @self.app.callback(
    #         [
    #             Output("odb_quantity-plot", "figure"),
    #             Output("odb_price-plot", "figure"),
    #             Output("odb_forstock-plot", "figure"),
    #         ],
    #         [
    #             Input("odb_region-dropdown", "value"),
    #             Input("odb_continent-dropdown", "value"),
    #             Input("odb_domain-dropdown", "value"),
    #             Input("odb_commodity-dropdown", "value"),
    #             Input("odb_commodity-group-dropdown", "value"),
    #             Input("odb_scenario-filter", "value"),
    #         ],
    #     )
    #     def update_plots(region, continent, domain, commodity, commodity_group, scenario):
    #         df = PlotUtils.filter_data(
    #             df=self.data.copy(),
    #             region=region,
    #             continent=continent,
    #             domain=domain,
    #             commodity=commodity,
    #             commodity_group=commodity_group,
    #             scenario=scenario,
    #         )
    #         df=self.remove_extreme_outliers(df, "price")

    #         forest_df = PlotUtils.filter_data(
    #             df=self.forest_data.copy(),
    #             region=region,
    #             continent=continent,
    #             domain=domain,
    #             commodity=commodity,
    #             commodity_group=commodity_group,
    #             scenario=scenario,
    #         )

    #         if not isinstance(df, pd.DataFrame):
    #             raise TypeError(
    #                 f"filter_data muss DataFrame liefern, "
    #                 f"bekommen: {type(df)}"
    #             )
            
    #         title_suffix = self.generate_title(
    #             region,
    #             continent,
    #             domain,
    #             commodity,
    #             commodity_group,
    #         )

    #         fig_quantity = self.plots.create_quantity_plot(
    #             df=df,
    #             start_year=self.start,
    #             end_year=self.end,
    #             plot_settings=self.plot_settings,
    #             title_suffix=title_suffix,
    #         )

    #         fig_price = self.plots.create_price_plot(df=df)
    #         fig_forstock = self.plots.plot_forstock(df=forest_df)

    #         return fig_quantity, fig_price, fig_forstock


    #     @self.app.callback(
    #         Output("odb_world-map", "figure"),
    #         [
    #             Input("odb_scenario-filter", "value"),
    #             Input("odb_year-filter", "value"),
    #             Input("odb_region-dropdown", "value"),
    #             Input("odb_continent-dropdown", "value"),
    #             Input("odb_domain-dropdown", "value"),
    #             Input("odb_commodity-dropdown", "value"),
    #             Input("odb_commodity-group-dropdown", "value"),
    #         ],
    #     )
    #     def update_world_map(scenario, year, region, continent, domain, commodity, commodity_group):
    #         df = PlotUtils.filter_data(
    #             df=self.data.copy(),
    #             region=region,
    #             continent=continent,
    #             domain=domain,
    #             commodity=commodity,
    #             commodity_group=commodity_group,
    #             scenario=scenario,
    #         )

    #         if year:
    #             df = df[df["year"] == year]

    #         title_suffix = self.generate_title(
    #             region, continent, domain, commodity, commodity_group
    #         )

    #         return self.plots.create_world_map_plot(df, title_suffix)

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