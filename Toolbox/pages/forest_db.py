import dash
import pandas as pd
import numpy as np
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# =====================================================
# DATA
# =====================================================

def drop_duplicates_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


# =====================================================
# COLOR HANDLING
# =====================================================

def get_scenario_colors(scenarios):
    base_colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c",
        "#d62728", "#9467bd", "#8c564b"
    ]
    return {s: base_colors[i % len(base_colors)] for i, s in enumerate(scenarios)}


# =====================================================
# PLOT FUNCTIONS
# =====================================================
def dynamic_y_range(values, lower_factor=0.9, upper_factor=1.1):
    values = pd.Series(values).dropna()
    if values.empty:
        return None
    return [
        values.min() * lower_factor,
        values.max() * upper_factor
    ]

def plot_forarea(df, colors):
    periods = sorted(df["Period"].unique())
    fig = go.Figure()

    all_values = []

    for s in df["Scenario"].unique():
        area = df[df["Scenario"] == s].groupby("Period")["ForArea"].sum()
        y_vals = [area.get(p, 0) for p in periods]
        all_values.extend(y_vals)

        fig.add_bar(
            x=periods,
            y=y_vals,
            marker_color=colors[s],
            showlegend=False
        )

    y_range = dynamic_y_range(all_values)

    fig.update_layout(
        title="Forest Area",
        xaxis_title="Period",
        yaxis_title="Sum of ForArea",
        barmode="group",
        template="plotly_white",
        yaxis=dict(range=y_range)
    )

    return fig


def plot_forstock(df, colors):
    periods = sorted(df["Period"].unique())
    fig = go.Figure()

    all_values = []

    for s in df["Scenario"].unique():
        stock = df[df["Scenario"] == s].groupby("Period")["ForStock"].sum()
        y_vals = [stock.get(p, 0) for p in periods]
        all_values.extend(y_vals)

        fig.add_bar(
            x=periods,
            y=y_vals,
            marker_color=colors[s],
            showlegend=False
        )

    y_range = dynamic_y_range(all_values)

    fig.update_layout(
        title="Forest Stock",
        xaxis_title="Period",
        yaxis_title="Sum of ForStock",
        barmode="group",
        template="plotly_white",
        yaxis=dict(range=y_range)
    )

    return fig



def plot_area_growth(df, colors):
    periods = sorted(df["Period"].unique())
    fig = go.Figure()
    for s in df["Scenario"].unique():
        area = df[df["Scenario"] == s].groupby("Period")["ForArea"].sum().reindex(periods)
        fig.add_scatter(x=periods, y=area.pct_change(),
                        mode="lines+markers",
                        line=dict(color=colors[s]), showlegend=False)
    fig.update_layout(title="Forest Area Growth",
                      xaxis_title="Period", yaxis_title="Growth rate",
                      yaxis_tickformat=".1%",
                      template="plotly_white")
    return fig


def plot_stock_growth(df, colors):
    periods = sorted(df["Period"].unique())
    fig = go.Figure()
    for s in df["Scenario"].unique():
        stock = df[df["Scenario"] == s].groupby("Period")["ForStock"].sum().reindex(periods)
        fig.add_scatter(x=periods, y=stock.pct_change(),
                        mode="lines+markers",
                        line=dict(color=colors[s]), showlegend=False)
    fig.update_layout(title="Forest Stock Growth",
                      xaxis_title="Period", yaxis_title="Growth rate",
                      yaxis_tickformat=".1%",
                      template="plotly_white")
    return fig


def plot_stock_area_ratio(df, colors):
    periods = sorted(df["Period"].unique())
    fig = go.Figure()
    for s in df["Scenario"].unique():
        g = df[df["Scenario"] == s].groupby("Period")[["ForStock", "ForArea"]].sum().replace(0, np.nan)
        ratio = g["ForStock"] / g["ForArea"]
        fig.add_scatter(x=periods, y=[ratio.get(p) for p in periods],
                        mode="lines+markers",
                        line=dict(color=colors[s]), showlegend=False)
    fig.update_layout(title="Stock / Area",
                      xaxis_title="Period", yaxis_title="Stock per Area",
                      template="plotly_white")
    return fig


def plot_supply_from_forest(df, colors):
    periods = sorted(df["Period"].unique())
    fig = go.Figure()

    for s in df["Scenario"].unique():
        sub = (
            df[df["Scenario"] == s]
            .sort_values("Period")
            .groupby("Period")[["supply_from_forest", "year"]]
            .sum()
            .reindex(periods)
        )

        delta_year = sub["year"].diff()
        normalized_supply = sub["supply_from_forest"] / delta_year

        fig.add_scatter(
            x=periods,
            y=normalized_supply,
            mode="lines+markers",
            line=dict(color=colors[s]),
            showlegend=False
        )

    fig.update_layout(
        title="Supply from Forest (per year change)",
        xaxis_title="Period",
        yaxis_title="Supply / ΔYear",
        template="plotly_white"
    )
    return fig


# =====================================================
# DASHBOARD
# =====================================================

class ForestDB:

    def __init__(self, app, data: pd.DataFrame):
        self.app = app
        self.data = drop_duplicates_df(data)
        self.scenarios = sorted(self.data["Scenario"].dropna().unique())
        self.colors = get_scenario_colors(self.scenarios)
        self.app_layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):

        legend_items = [
            html.Div(
                style={"display": "flex", "alignItems": "center", "margin": "0 14px"},
                children=[
                    html.Div(style={
                        "width": "14px",
                        "height": "14px",
                        "backgroundColor": self.colors[s],
                        "marginRight": "6px"
                    }),
                    html.Span(s)
                ]
            ) for s in self.scenarios
        ]

        return dbc.Container(fluid=True, children=[

            # ===== FILTER BAR =====
            dbc.Card(
                className="border-0 shadow-sm mb-2",
                body=True,
                children=[
                    dbc.Row(className="g-3", children=[
                        dbc.Col(
                            dcc.Dropdown(
                                id="fdb_continent-dropdown",
                                options=[{"label": c, "value": c}
                                         for c in sorted(self.data["Continent"].dropna().unique())],
                                multi=True,
                                placeholder="Continent"
                            ),
                            width=4
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="fdb_country-dropdown",
                                options=[{"label": c, "value": c}
                                         for c in sorted(self.data["ISO3"].dropna().unique())],
                                multi=True,
                                placeholder="Country (ISO3)"
                            ),
                            width=4
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="fdb_scenario-dropdown",
                                options=[{"label": "All", "value": "All"}] +
                                        [{"label": s, "value": s} for s in self.scenarios],
                                multi=True,
                                placeholder="Scenario"
                            ),
                            width=4
                        )
                    ])
                ]
            ),

            # ===== 3x2 GRID =====
            html.Div(style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr 1fr",
                "gridTemplateRows": "1fr 1fr",
                "gap": "10px"
            }, children=[
                dcc.Graph(id="g_area"),
                dcc.Graph(id="g_area_growth"),
                dcc.Graph(id="g_ratio"),
                dcc.Graph(id="g_stock"),
                dcc.Graph(id="g_stock_growth"),
                dcc.Graph(id="g_supply"),
            ]),

            # ===== GLOBAL LEGEND =====
            dbc.Card(
                className="border-0 mt-2",
                body=True,
                children=[
                    html.Div(
                        legend_items,
                        style={"display": "flex", "justifyContent": "center", "flexWrap": "wrap"}
                    )
                ]
            )
        ])

    def register_callbacks(self):

        @self.app.callback(
            Output("g_area", "figure"),
            Output("g_stock", "figure"),
            Output("g_area_growth", "figure"),
            Output("g_stock_growth", "figure"),
            Output("g_ratio", "figure"),
            Output("g_supply", "figure"),
            Input("fdb_scenario-dropdown", "value"),
            Input("fdb_country-dropdown", "value"),
            Input("fdb_continent-dropdown", "value"),
        )
        def update_graphs(scenarios, countries, continents):

            df = self.data.copy()

            if scenarios and "All" not in scenarios:
                df = df[df["Scenario"].isin(scenarios)]

            if countries:
                df = df[df["ISO3"].isin(countries)]

            if continents:
                df = df[df["Continent"].isin(continents)]

            return (
                plot_forarea(df, self.colors),
                plot_forstock(df, self.colors),
                plot_area_growth(df, self.colors),
                plot_stock_growth(df, self.colors),
                plot_stock_area_ratio(df, self.colors),
                plot_supply_from_forest(df, self.colors),
            )
