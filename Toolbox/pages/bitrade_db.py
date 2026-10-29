import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, ctx
from dash.dependencies import Input, Output, State
import pandas as pd
from Toolbox.classes.utils import PlotUtils
from Toolbox.classes.PlotManager import Plots
from Toolbox.classes.LayoutManager import Layout, FilterLayout
from Toolbox.parameters.filter_config import BILATERAL_TRADE_DB_FILTERS
import Toolbox.parameters.layout_styles as ls
from datetime import datetime
from Toolbox.classes.ring_plot_utils import RingPlotsUtils


class BiTradeDB:
     
    def __init__(self, 
                 app, 
                 data: pd.DataFrame,
                 colors):
        self.app = app
        self.db_prefix = "tdb"
        self.data = data
        self.filters = BILATERAL_TRADE_DB_FILTERS
        self.plots = Plots()
        self.layout = Layout()
        self.filter_builder = FilterLayout(self.data, prefix=self.db_prefix)
        self.scenarios = sorted(self.data["Scenario"].dropna().unique())
        self.colors = colors
        self.app_layout = self.create_layout()
        self.register_callbacks()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def create_layout(self):

        filters = self.filter_builder.build_all(self.filters)
        button = self.layout.download_button(f"{self.db_prefix}_download-btn")

        return dbc.Container(
            fluid=True,
            style=ls.outer_card_under_header,
            # ==========================================================
            # Card for filter bar
            # ==========================================================
            children=[
                dcc.Store(
                    id="tbd_scenario_index",
                    data=0,
                ),
                dbc.Card(
                    className="border-1 shadow-sm",
                    style=ls.filter_card_background,
                    body=True,
                    children=[
                        html.Div(
                            style=ls.filter_inner_card,
                            children = filters + button
                        ),
                    ]
                ),
                # ==========================================================
                # Card behind all plots
                # ==========================================================
                html.Div(
                    style=ls.plot_card_3x2_background_main,
                    children=[
                        #-----------
                        # Cards for the specific plots
                        #-----------

                        self.layout._graph_card("tbd_import_q"),
                        html.Div(
                            children=[
                                self.layout._graph_card("tbd_rad_tile"),

                                html.Button(
                                    "←",
                                    id="tbd_rad_prev",
                                    n_clicks=0,
                                    className="rad-arrow rad-arrow-left",
                                ),

                                html.Span(
                                    id="tbd_scenario_label",
                                    children="",
                                    className="rad-scenario-label",
                                ),

                                html.Button(
                                    "→",
                                    id="tbd_rad_next",
                                    n_clicks=0,
                                    className="rad-arrow rad-arrow-right",
                                ),
                                dbc.RadioItems(
                                            id="tbd_trade_type",
                                            options=[
                                                {"label": "Export", "value": "Export"},
                                                {"label": "Import", "value": "Import"},
                                            ],
                                            value="Export",
                                            inline=True,
                                            className="trade-toggle",
                                            inputClassName="btn-check",
                                            labelClassName="btn btn-outline-secondary",
                                            labelCheckedClassName="btn trade-toggle-active",
                                ),
                                dbc.RadioItems(
                                            id="tbd_country_type",
                                            options=[
                                                {"label": "Countries", "value": "Countries"},
                                                {"label": "Continents", "value": "Continents"},
                                            ],
                                            value="Countries",
                                            inline=True,
                                            className="country-toggle",
                                            inputClassName="btn-check",
                                            labelClassName="btn btn-outline-secondary",
                                            labelCheckedClassName="btn country-toggle-active",
                                ),
                            ],
                            style={
                                **ls.main_plot_card,
                                "position": "relative",
                            },
                        ),
                        self.layout._graph_card("tbd_export_q"),
                        self.layout._graph_card("tbd_import_nt"),
                        self.layout._graph_card("tbd_export_nt"),
                    ]
                ),

                # ==========================================================
                # Card for the legend
                # ==========================================================
                self.layout._legend_card(colors= self.colors,
                                         scenarios = self.scenarios),
                dcc.Download(id=f"{self.db_prefix}_download")
            ]
        )
    
    
    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def register_callbacks(self):
        filter_inputs = PlotUtils().build_filter_inputs(
            self.db_prefix, 
            self.filters
        )

        @self.app.callback(
            Output("tbd_import_q", "figure"),
            Output("tbd_rad_tile", "figure"),
            Output("tbd_export_q", "figure"),
            Output("tbd_import_nt", "figure"),
            Output("tbd_export_nt", "figure"),
            Output("tbd_scenario_index", "data"),
            Output("tbd_scenario_label", "children"),
            Output("tbd_rad_prev", "style"),
            Output("tbd_rad_next", "style"),
            Input("tbd_rad_prev", "n_clicks"),
            Input("tbd_rad_next", "n_clicks"),
            Input("tbd_trade_type", "value"),
            Input("tbd_country_type", "value"),
            *filter_inputs,
            State("tbd_scenario_index", "data"),
        )

        def update_plots(prev_clicks, next_clicks, trade_type, country_type, *args):
            filter_values = args[:-1]
            scenario_id = args[-1] or 0
            print(trade_type)
            print(country_type)

            print(f"{self.db_prefix}_dashboard")
            filter_values_dict = dict(zip(self.filters.keys(), filter_values))
            print(filter_values_dict)
            #-----------
            # subset for net export
            #-----------
            df = PlotUtils.filter_data(
                df=self.data.copy(),
                **PlotUtils().get_plot_filters(
                    filter_values_dict, 
                    "bilateral_trade"
                )
            )
            
            scen_list = sorted(df["Scenario"].dropna().unique())
            n_scenarios = len(scen_list)

            triggered_id = ctx.triggered_id

            if n_scenarios > 0:
                if triggered_id == "tbd_rad_prev":
                    scenario_id = max(0, scenario_id - 1)

                elif triggered_id == "tbd_rad_next":
                    scenario_id = min(n_scenarios - 1, scenario_id + 1)
            else:
                scenario_id = 0

            prev_style = {
                "display": "none" if scenario_id <= 0 else "block"
            }

            next_style = {
                "display": "none"
                if n_scenarios == 0 or scenario_id >= n_scenarios - 1
                else "block"
            }

            # ---------------------------------------------------------
            #filter export data
            exp_filter_dict = filter_values_dict.copy()
            del_imp = ["importer", "importer_continent"]
            for key in list(del_imp):
                exp_filter_dict.pop(key, None)

            exp_df = self.data.copy()
            exp_df = PlotUtils.filter_data(
                df=exp_df,
                **PlotUtils().get_plot_filters(
                    exp_filter_dict, 
                    "bilateral_trade"
                )
            )
            export_index = ["Exporter","Continent_Exporter","Commodity","Commodity_Group","Scenario","year"]
            export_q = (
                exp_df.groupby(export_index, observed=True, dropna=False).agg({
                    "total_export": "mean",
                    "total_nettrade": "sum",
                }).reset_index()
            )

            #filter import data
            imp_filter_dict = filter_values_dict.copy()
            del_exp = ["exporter", "exporter_continent"]
            for key in list(del_exp):
                imp_filter_dict.pop(key, None)

            imp_df = self.data.copy()
            imp_df = PlotUtils.filter_data(
                df=imp_df,
                **PlotUtils().get_plot_filters(
                    imp_filter_dict, 
                    "bilateral_trade"
                )
            )
            import_index = ["Importer","Continent_Importer","Commodity","Commodity_Group","Scenario","year"]
            import_q = (
                imp_df.groupby(import_index, observed=True, dropna=False).agg({
                    "total_import": "mean",
                    "total_nettrade": "sum",
                }).reset_index()
            )

            title = PlotUtils.generate_title(
                filter_dict=filter_values_dict,
            )

            exp_title = PlotUtils.generate_title(
                filter_dict=exp_filter_dict,
            )

            imp_title = PlotUtils.generate_title(
                filter_dict=imp_filter_dict,
            )

            # ---------------------------------------------------------

            # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            def _top_countries(
                df: pd.DataFrame,
                YearColumn: str,
                CountryColumn: str,
                ValueColumn: str
            ):
                d = df[[YearColumn, CountryColumn, ValueColumn]].copy()

                totals = d.groupby([YearColumn, CountryColumn])[ValueColumn].sum().reset_index()
                totals["rank"] = totals.groupby(YearColumn)[ValueColumn].rank(method="first", ascending=False)
                top_map = totals.loc[
                    totals["rank"] <= 5,
                    [YearColumn, CountryColumn]
                ].assign(
                    helper=lambda x: x[YearColumn].astype(str) + x[CountryColumn].astype(str)
                )["helper"]

                d["helper"] = d[YearColumn].astype(str) + d[CountryColumn].astype(str)
                d.loc[~d["helper"].isin(top_map), CountryColumn] = "RoW"
                
                top = d[CountryColumn].unique()
                top = top[top!="RoW"]

                g = d.groupby([YearColumn, CountryColumn])[ValueColumn].sum().reset_index()
                g = g[g[ValueColumn] != 0]
                pivot = g.pivot(index=YearColumn,columns=CountryColumn,values=ValueColumn).fillna(0.0).sort_index()

                return pivot, top

            #**********************************************

            def _check_center_label(
                    country_column:str,
                    continent_column:str,
                    alt_label:str,
            )->str:
                if len(df[country_column].unique()) <= 3:
                    return ", ".join(df[country_column].unique())
                elif len(df[continent_column].unique()) <= 3:
                    return "_".join(df[continent_column].unique())
                else:
                    return alt_label
                
            try:
                df_ring_sc1 = df[df["Scenario"]==df["Scenario"].unique()[scenario_id]]
                scenario = df["Scenario"].unique()[scenario_id]

                exporter=_check_center_label(
                    country_column="Exporter",
                    continent_column="Continent_Exporter",
                    alt_label="World",
                )

                importer=_check_center_label(
                    country_column="Importer",
                    continent_column="Continent_Importer",
                    alt_label="...",
                )

                center_label = f"{exporter}<br> to <br>{importer}"
                    

                pivot_export_country_sc1, top_export_country_sc1 = _top_countries(
                    df=df_ring_sc1,
                    YearColumn="year",
                    CountryColumn="Importer",
                    ValueColumn="trade_flow",
                )

                fig_rad_tile = Plots().create_trade_ring_plot(
                    pivot=pivot_export_country_sc1, 
                    top=top_export_country_sc1, 
                    center_label=center_label
                )
            except IndexError:
                fig_rad_tile = PlotUtils.placeholder_figure("No bilateral data")


            fig_agg_export = self.plots.create_trade_line_plot(
                df=export_q,
                trade_domain="total_export",
                colors=self.colors,
                title=exp_title,
                y_label="",
            )
            fig_agg_import = self.plots.create_trade_line_plot(
                df=import_q,
                trade_domain="total_import",
                colors=self.colors,
                title=imp_title,
                y_label="",
            )

            q_net_export_fig = self.plots.create_trade_bar_plot(
                df=export_q,
                trade_domain="total_nettrade",
                unit="total_nettrade",
                colors=self.colors,
                title=title,
                y_label="",
            )

            q_net_import_fig = self.plots.create_trade_bar_plot(
                df=import_q,
                trade_domain="total_nettrade",
                unit="total_nettrade",
                colors=self.colors,
                title=title,
                y_label="",
            )

            return (
                fig_agg_export,
                fig_rad_tile,
                fig_agg_import,
                q_net_export_fig,
                q_net_import_fig, 
                scenario_id,
                str(scenario) if scenario is not None else "No scenario found",
                prev_style,
                next_style,
            )

        # ---------------------------
        # Download CSV
        # ---------------------------
        filter_states = [
            State(f"{self.db_prefix}_{key}-dropdown", "value")
            for key in self.filters.keys()
        ]

        @self.app.callback(
            Output(f"{self.db_prefix}_download", "data"),
            Input(f"{self.db_prefix}_download-btn", "n_clicks"),
            *filter_states,
            prevent_initial_call=True
        )

        def download_filtered_csv(n_clicks, *filter_values):
            if n_clicks is None:
                return dash.no_update
            
            filter_values_dict = dict(zip(self.filters.keys(), filter_values))

            df = PlotUtils.filter_data(
                df=self.data.copy(),
                **filter_values_dict
            )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            return dcc.send_data_frame(
                df.to_csv,
                f"filtered_data_{timestamp}.csv",
                index=False
            )
        