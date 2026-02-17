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

        options = [
            {"label": c, "value": c}
            for c in sorted(self.data[column].dropna().unique())
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
