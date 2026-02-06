import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import textwrap
from Toolbox.classes.utils import PlotUtils

class Plots:

    def __init__(self, template="plotly_white"):
        self.template = template

    def create_quantity_plot(self, df, start_year, end_year, plot_settings, title_suffix):
        grouped_df = df.groupby(["year", "Scenario"]).sum().reset_index()
        grouped_df = grouped_df[(grouped_df["year"] >= start_year) & (grouped_df["year"] <= end_year)]
        colors = PlotUtils.get_scenario_colors(scenarios=grouped_df["Scenario"].unique())

        fig = go.Figure()
        for i, scenario in enumerate(grouped_df["Scenario"].unique()):
            subset = grouped_df[grouped_df["Scenario"] == scenario]
            dash = "solid" if scenario == "Historic Data" else "dash"
            fig.add_trace(go.Scatter(
                x=subset["year"], y=subset["quantity"]*1000,
                mode="lines", name=scenario,
                line=dict(color=colors[scenario], dash=dash, width=plot_settings["line_witdh"])
            ))

        title = f"Quantity by Year and Scenario for {title_suffix}"
        fig.update_layout(
            title=dict(text="<br>".join(textwrap.wrap(title, 90)),
                       font=dict(size=plot_settings["title_font_size"])),
            xaxis=dict(title="Year", tickfont=dict(size=plot_settings["tick_font_size"])),
            yaxis=dict(title="Quantity", rangemode="nonnegative",
                       tickfont=dict(size=plot_settings["tick_font_size"])),
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center",
                        font=dict(size=plot_settings["legend_font_size"])),
            hovermode="x unified",
            template=self.template,
            margin=dict(l=35, r=35, t=60, b=90)
        )
        return fig

    def create_price_plot(self, df):
        grouped = df.groupby(["year", "Scenario"]).mean().reset_index()
        colors = PlotUtils.get_scenario_colors(scenarios=grouped["Scenario"].unique())

        fig = go.Figure()
        for i, scenario in enumerate(grouped["Scenario"].unique()):
            subset = grouped[grouped["Scenario"] == scenario]
            fig.add_trace(go.Bar(
                x=subset["price"], y=subset["year"],
                orientation="h", name=scenario,
                marker_color=colors[scenario]
            ))
        fig.update_layout(
            title="Price by Period and Scenario",
            xaxis_title="Price",
            yaxis_title="Year",
            template=self.template,
            showlegend=False,
            margin=dict(l=35, r=60, t=50, b=5),
            barmode="group"
        )
        return fig

    def create_forstock_plot(self, df):
        stock = df.drop(columns=[
            "domain","price","quantity","CommodityCode","Commodity","Commodity_Group"
        ]).drop_duplicates().groupby(["year", "Scenario"]).agg({"ForStock":"sum"}).reset_index()
        stock = stock[stock["Scenario"] != "Historic Data"]
        colors = PlotUtils.get_scenario_colors(scenarios=stock["Scenario"].unique())

        fig = go.Figure()
        for i, scenario in enumerate(stock["Scenario"].unique()):
            subset = stock[stock["Scenario"] == scenario]
            fig.add_trace(go.Bar(
                x=subset["year"], y=subset["ForStock"],
                name=scenario, marker_color=colors[scenario]
            ))
        fig.update_layout(
            title="Forest Stock by Year and Scenario",
            xaxis_title="Year",
            yaxis_title="ForStock",
            template=self.template,
            showlegend=False,
            margin=dict(l=50, r=50, t=40, b=5),
            barmode="group"
        )
        return fig

    def create_world_map_plot(self, filtered_data, title_suffix):
        country_data = filtered_data.groupby("ISO3")["quantity"].sum().reset_index()
        country_data = country_data[country_data["quantity"] >= 0.001]
        fig = px.choropleth(country_data, locations="ISO3", color="quantity",
                            hover_name="ISO3", color_continuous_scale="Greens")
        fig.update_layout(
            title=f"Worldmap for {title_suffix}",
            geo=dict(showcoastlines=True, coastlinecolor="LightGray",
                     projection_type="natural earth", lonaxis_range=[-360,360], lataxis_range=[-55,55]),
            margin=dict(l=1,r=1,t=1,b=1),
            coloraxis_showscale=False
        )
        return fig

    def plot_forarea(self, df):
        periods = sorted(df["Period"].unique())
        colors = PlotUtils.get_scenario_colors(scenarios=df["Scenario"].unique())

        fig = go.Figure()
        all_values = []
        for s in df["Scenario"].unique():
            area = df[df["Scenario"]==s].groupby("Period")["ForArea"].sum()
            y_vals = [area.get(p,0) for p in periods]
            all_values.extend(y_vals)
            fig.add_bar(x=periods, y=y_vals, marker_color=colors[s], showlegend=False)
        fig.update_layout(
            title="Forest Area", xaxis_title="Period", yaxis_title="Sum of ForArea",
            barmode="group", template=self.template, yaxis=dict(range=PlotUtils.dynamic_y_range(all_values))
        )
        return fig

    def plot_forstock(self, df):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        all_values = []
        colors = PlotUtils.get_scenario_colors(scenarios=df["Scenario"].unique())
        for s in df["Scenario"].unique():
            stock = df[df["Scenario"]==s].groupby("Period")["ForStock"].sum()
            y_vals = [stock.get(p,0) for p in periods]
            all_values.extend(y_vals)
            fig.add_bar(x=periods, y=y_vals, marker_color=colors[s], showlegend=False)
        fig.update_layout(
            title="Forest Stock", xaxis_title="Period", yaxis_title="Sum of ForStock",
            barmode="group", template=self.template, yaxis=dict(range=PlotUtils.dynamic_y_range(all_values))
        )
        return fig

    def plot_area_growth(self, df):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        colors = PlotUtils.get_scenario_colors(scenarios=df["Scenario"].unique())
        for s in df["Scenario"].unique():
            area = df[df["Scenario"]==s].groupby("Period")["ForArea"].sum().reindex(periods)
            fig.add_scatter(x=periods, y=area.pct_change(), mode="lines+markers",
                            line=dict(color=colors[s]), showlegend=False)
        fig.update_layout(title="Forest Area Growth",
                          xaxis_title="Period", yaxis_title="Growth rate",
                          yaxis_tickformat=".1%", template=self.template)
        return fig

    def plot_stock_growth(self, df):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        colors = PlotUtils.get_scenario_colors(scenarios=df["Scenario"].unique())
        for s in df["Scenario"].unique():
            stock = df[df["Scenario"]==s].groupby("Period")["ForStock"].sum().reindex(periods)
            fig.add_scatter(x=periods, y=stock.pct_change(), mode="lines+markers",
                            line=dict(color=colors[s]), showlegend=False)
        fig.update_layout(title="Forest Stock Growth",
                          xaxis_title="Period", yaxis_title="Growth rate",
                          yaxis_tickformat=".1%", template=self.template)
        return fig

    def plot_stock_area_ratio(self, df):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        colors = PlotUtils.get_scenario_colors(scenarios=df["Scenario"].unique())
        for s in df["Scenario"].unique():
            g = df[df["Scenario"]==s].groupby("Period")[["ForStock","ForArea"]].sum().replace(0,np.nan)
            ratio = g["ForStock"]/g["ForArea"]
            fig.add_scatter(x=periods, y=[ratio.get(p) for p in periods],
                            mode="lines+markers", line=dict(color=colors[s]), showlegend=False)
        fig.update_layout(title="Stock / Area", xaxis_title="Period", yaxis_title="Stock per Area",
                          template=self.template)
        return fig

    def plot_supply_from_forest(self, df):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        colors = PlotUtils.get_scenario_colors(scenarios=df["Scenario"].unique())
        for s in df["Scenario"].unique():
            sub = df[df["Scenario"]==s].sort_values("Period").groupby("Period")[["supply_from_forest","year"]].sum().reindex(periods)
            delta_year = sub["year"].diff()
            normalized_supply = sub["supply_from_forest"]/delta_year
            fig.add_scatter(x=periods, y=normalized_supply, mode="lines+markers",
                            line=dict(color=colors[s]), showlegend=False)
        fig.update_layout(title="Supply from Forest (per year change)", xaxis_title="Period",
                          yaxis_title="Supply / ΔYear", template=self.template)
        return fig
