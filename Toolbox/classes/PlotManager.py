import pandas as pd
import numpy as np
import plotly.graph_objects as go

class forestplots():

    def __init__(self,data):
        self.data=data

    def get_scenario_colors(self,scenarios):
        base_colors = [
            "#1f77b4", "#ff7f0e", "#2ca02c",
            "#d62728", "#9467bd", "#8c564b"
        ]
        return {s: base_colors[i % len(base_colors)] for i, s in enumerate(scenarios)}

    def dynamic_y_range(self,values, lower_factor=0.9, upper_factor=1.1):
        values = pd.Series(values).dropna()
        if values.empty:
            return None
        return [
            values.min() * lower_factor,
            values.max() * upper_factor
        ]

    def plot_forarea(self,df, colors):
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

        y_range = self.dynamic_y_range(all_values)

        fig.update_layout(
            title="Forest Area",
            xaxis_title="Period",
            yaxis_title="Sum of ForArea",
            barmode="group",
            template="plotly_white",
            yaxis=dict(range=y_range)
        )

        return fig


    def plot_forstock(self, df, colors):
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
        y_range = self.dynamic_y_range(all_values)

        fig.update_layout(
            title="Forest Stock",
            xaxis_title="Period",
            yaxis_title="Sum of ForStock",
            barmode="group",
            template="plotly_white",
            yaxis=dict(range=y_range)
        )
        return fig

    def plot_area_growth(self, df, colors):
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


    def plot_stock_growth(self, df, colors):
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


    def plot_stock_area_ratio(self, df, colors):
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


    def plot_supply_from_forest(self, df, colors):
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
