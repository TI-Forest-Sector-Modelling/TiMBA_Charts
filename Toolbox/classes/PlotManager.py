import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import textwrap

import plotly.graph_objects as go
import plotly.express as px
import textwrap


class overviewplots:
    """
    Collection of static plot helper methods for the Overview Dashboard.
    All methods expect a pandas DataFrame as input and return a Plotly Figure.
    """

    def __init__(self):
        pass

    @staticmethod
    def create_quantity_plot(
        filtered_data,
        start_year,
        end_year,
        color_list,
        plot_settings,
        title_suffix,
        graphic_template="plotly_white",
    ):
        grouped = (
            filtered_data
            .groupby(["year", "Scenario"])
            .sum()
            .reset_index()
        )

        grouped = grouped[
            (grouped["year"] >= start_year) &
            (grouped["year"] <= end_year)
        ]

        fig = go.Figure()

        for i, scenario in enumerate(grouped["Scenario"].unique()):
            subset = grouped[grouped["Scenario"] == scenario]
            color = color_list[i % len(color_list)]
            dash = "solid" if scenario == "Historic Data" else "dash"

            fig.add_trace(
                go.Scatter(
                    x=subset["year"],
                    y=subset["quantity"] * 1000,
                    mode="lines",
                    name=scenario,
                    line=dict(
                        color=color,
                        dash=dash,
                        width=plot_settings["line_witdh"],
                    ),
                )
            )

        title = f"Quantity by Year and Scenario for {title_suffix}"

        fig.update_layout(
            title=dict(
                text="<br>".join(textwrap.wrap(title, 90)),
                font=dict(size=plot_settings["title_font_size"]),
            ),
            xaxis=dict(
                title="Year",
                tickfont=dict(size=plot_settings["tick_font_size"]),
            ),
            yaxis=dict(
                title="Quantity",
                rangemode="nonnegative",
                tickfont=dict(size=plot_settings["tick_font_size"]),
            ),
            legend=dict(
                orientation="h",
                y=-0.1,
                x=0.5,
                xanchor="center",
                font=dict(size=plot_settings["legend_font_size"]),
            ),
            hovermode="x unified",
            template=graphic_template,
            margin=dict(l=35, r=35, t=60, b=90),
        )

        return fig

    @staticmethod
    def create_price_plot(
        filtered_data,
        color_list,
        graphic_template="plotly_white",
    ):
        grouped = (
            filtered_data
            .groupby(["year", "Scenario"])
            .mean()
            .reset_index()
        )

        fig = go.Figure()

        for i, scenario in enumerate(grouped["Scenario"].unique()):
            subset = grouped[grouped["Scenario"] == scenario]
            color = color_list[i % len(color_list)]

            fig.add_trace(
                go.Bar(
                    x=subset["price"],
                    y=subset["year"],
                    orientation="h",
                    name=scenario,
                    marker_color=color,
                )
            )

        fig.update_layout(
            title="Price by Period and Scenario",
            xaxis_title="Price",
            yaxis_title="Year",
            template=graphic_template,
            showlegend=False,
            margin=dict(l=35, r=60, t=50, b=5),
            barmode="group",
        )

        return fig

    @staticmethod
    def create_forstock_plot(
        filtered_data,
        color_list,
        graphic_template="plotly_white",
    ):
        stock = (
            filtered_data
            .drop(
                columns=[
                    "domain",
                    "price",
                    "quantity",
                    "CommodityCode",
                    "Commodity",
                    "Commodity_Group",
                ]
            )
            .drop_duplicates()
            .groupby(["year", "Scenario"])
            .agg({"ForStock": "sum"})
            .reset_index()
        )

        stock = stock[stock["Scenario"] != "Historic Data"]

        fig = go.Figure()

        for i, scenario in enumerate(stock["Scenario"].unique()):
            subset = stock[stock["Scenario"] == scenario]
            color = color_list[i % len(color_list)]

            fig.add_trace(
                go.Bar(
                    x=subset["year"],
                    y=subset["ForStock"],
                    name=scenario,
                    marker_color=color,
                )
            )

        fig.update_layout(
            title="Forest Stock by Year and Scenario",
            xaxis_title="Year",
            yaxis_title="ForStock",
            template=graphic_template,
            showlegend=False,
            margin=dict(l=50, r=50, t=40, b=5),
            barmode="group",
        )

        return fig

    @staticmethod
    def create_world_map_plot(
        filtered_data,
        title_suffix,
    ):
        country_data = (
            filtered_data
            .groupby("ISO3")["quantity"]
            .sum()
            .reset_index()
        )

        country_data = country_data[country_data["quantity"] >= 0.001]

        fig = px.choropleth(
            country_data,
            locations="ISO3",
            color="quantity",
            hover_name="ISO3",
            color_continuous_scale="Greens",
        )

        fig.update_layout(
            title=f"Worldmap for {title_suffix}",
            geo=dict(
                showcoastlines=True,
                coastlinecolor="LightGray",
                projection_type="natural earth",
                lonaxis_range=[-360, 360],
                lataxis_range=[-55, 55],
            ),
            margin=dict(l=1, r=1, t=1, b=1),
            coloraxis_showscale=False,
        )

        return fig


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