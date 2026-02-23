from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import Toolbox.parameters.layout_styles as ls

class Layout:

    def __init__(self):
        pass

    @staticmethod
    def _graph_card(graph_id):
        '''
        Function that builds the cards for any plot
        '''
        return html.Div(
            dcc.Graph(
                id=graph_id,
                style={"height": "100%"},
                config={"responsive": True}
            ),
            style=ls.plot_card
        )
    
    @staticmethod
    def download_button(button_id):
        return[
            html.Div(
                dbc.Button(
                    "⬇ CSV",
                    id=button_id,
                    color="primary",
                    style={"height": "38px"}
                ),
                style={"flex": "1"}
            )
        ]

    
    @staticmethod
    def _legend_card(colors, scenarios):
        return dbc.Card(
            className="border-1 shadow-sm",
            style=ls.legend_card_background,
            body=True,
            children=[
                html.Div(
                    Layout.ledgend_items(colors, scenarios),
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "flexWrap": "wrap"
                    }
                )
            ]
        )
    
    @staticmethod
    def _legend_card_world_map():
        return dbc.Card(
            className="border-1 shadow-sm",
            style=ls.legend_card_background,
            body=True,
            children=[

                html.Div([
                    html.Div(
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "space-between",
                        },
                        children=[
                            # ---------- FIXED TEXT COLUMN ----------
                            html.Div(
                                "Alternative minus Reference scenario.",
                                style={
                                    "fontSize": "18px",
                                    "marginRight": "15px",
                                    "whiteSpace": "nowrap",
                                }
                            ),
                            html.Div(
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "width": "500px"   # <- kontrolliert Größe
                                },
                                children=[

                                    # Gradient Bar
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "height": "13px",
                                            "borderRadius": "4px",
                                            "background": "linear-gradient(to right, red, white, green)",
                                            "marginBottom": "2px",
                                            "marginLeft": "45px"
                                        }
                                    ),

                                    # Labels
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "fontSize": "12px",
                                            "marginLeft": "55px"
                                        },
                                        children=[
                                            html.Span("- (decrease compared to refernce)"),
                                            html.Span("0"),
                                            html.Span("(increase compared to refernce) +")
                                        ]
                                    )
                                ]
                            ),

                            # -------- Scenario Text --------
                            html.Div(
                                id="wmdb_legend_scenario_text",
                                children="REF: - | ALT: -",
                                style={
                                    "fontSize": "18x",
                                    "marginLeft": "15px",
                                    "whiteSpace": "nowrap"
                                }
                            )
                        ]
                    )
                ])
            ]
        )
    
    @staticmethod
    def ledgend_items(colors, scenarios):
        return[
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
                            "backgroundColor": colors[s],
                            "marginRight": "6px"
                        }
                    ),
                    html.Span(s)
                ]
            )
            for s in scenarios
        ]


class FilterLayout:

    def __init__(self, data:pd.DataFrame, prefix:str):
        self.data = data
        self.prefix = prefix

    def build_dropdown(self, key, config):

        column = config["column"]
        placeholder = config["placeholder"]

        if column in self.data.columns:
            options = [
                {"label": c, "value": c}
                for c in sorted(self.data[column].dropna().unique())
            ]
        else:
            options = [
                {"label": c, "value": c}
                for c in sorted(self.data.columns[6:])
            ]

        return html.Div(
            dcc.Dropdown(
                id=f"{self.prefix}_{key}-dropdown",
                options=options,
                multi=True,
                placeholder=placeholder
            ),
            style={"flex": "3"}
        )

    def build_all(self, filter_config):

        return [
            self.build_dropdown(key, config)
            for key, config in filter_config.items()
        ]
