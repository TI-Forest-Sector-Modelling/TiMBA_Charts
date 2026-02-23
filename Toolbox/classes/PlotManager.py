import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import textwrap
from Toolbox.classes.utils import PlotUtils

class Plots:

    def __init__(self, template="plotly_white"):
        self.template = template

    def create_quantity_plot(self, df,colors
                             ):
        grouped_df = df.groupby(["year", "Scenario"]).sum().reset_index()

        fig = go.Figure()
        for i, scenario in enumerate(grouped_df["Scenario"].unique()):
            subset = grouped_df[grouped_df["Scenario"] == scenario]
            dash = "solid" if scenario == "Historic Data" else "dash"
            fig.add_trace(
                go.Scatter(
                    x=subset["year"], 
                    y=subset["quantity"]*1000,
                    mode="lines", 
                    name=scenario,
                    line=dict(color=colors.get(scenario), 
                    )
                )
            )

        title = f"Quantity by Year and Scenario for"
        fig.update_layout(
            showlegend=False,
            title=dict(
                text="<br>".join(textwrap.wrap(title, 90)),
            ),
            xaxis=dict(
                title="Year", 
            ),
            yaxis=dict(
                title="Quantity in 1000 m³ or 1000 t", 
                rangemode="nonnegative",
            ),
            hovermode="x unified",
            template=self.template,
            autosize = True,
            margin=dict(l=40, r=20, t=40, b=40),
        )
        return fig

    def create_value_plot(self, df: pd.DataFrame,colors:dict) -> go.Figure:
        fig = go.Figure()
        plot_df = (
            df.groupby(["Scenario", "Period"], as_index=False)["Value"]
              .sum())

        for scenario in plot_df["Scenario"].unique():
            scenario_df = plot_df[plot_df["Scenario"] == scenario]

            fig.add_trace(
                go.Bar(
                    x=scenario_df["Period"],
                    y=scenario_df["Value"],
                    name=scenario,
                    marker=dict(color=colors.get(scenario)),
                )
            )

        fig.update_layout(
            title="Total Value over Time",
            xaxis_title="Period",
            yaxis_title="Value in 1000 US$",
            template="plotly_white",
            barmode="group",
            margin=dict(l=40, r=20, t=40, b=40),
            hovermode="x unified",
            showlegend=False
        )

        return fig
    
    def create_value_growth_plot(self, df: pd.DataFrame,colors:dict) -> go.Figure:
        fig = go.Figure()

        df["Prev_Value"] = df.groupby("Scenario")["Value"].shift(1)
        df["Prev_Year"] = df.groupby("Scenario")["year"].shift(1)

        df["Year_Diff"] = df["year"] - df["Prev_Year"]

        df["Annual_Growth"] = (
            (df["Value"] / df["Prev_Value"]) ** (1 / df["Year_Diff"]) - 1
        ) * 100

        for scenario in df["Scenario"].unique():
            scenario_df = df[df["Scenario"] == scenario]

            fig.add_trace(
                go.Scatter(
                    x=scenario_df["Period"],
                    y=scenario_df["Annual_Growth"],
                    name=scenario,
                    marker_color=colors.get(scenario),
                    mode="lines+markers", #only with scatter or line plot
                    line=dict(width=2,color=colors.get(scenario)),
                    )
            )

        fig.update_layout(
            title="Value growth per year",
            xaxis_title="Period",
            yaxis_title="Growth in %",
            template="plotly_white",
            margin=dict(l=40, r=20, t=40, b=40),
            hovermode="x unified",
            showlegend=False
        )

        return fig

    def create_price_plot(self, df: pd.DataFrame,colors:dict) -> go.Figure:
        fig = go.Figure()
        df = (
            df.groupby(["Scenario", "Period"], as_index=False)
              .agg({
                  "Value": "sum",
                  "quantity": "sum"
              })
        )
        df["Price"] = np.where(
            df["quantity"] > 0,
            df["Value"] / df["quantity"],
            np.nan
        )

        for scenario in df["Scenario"].unique():
            scenario_df = df[df["Scenario"] == scenario]

            fig.add_trace(
                go.Scatter(
                    x=scenario_df["Period"],
                    y=scenario_df["Price"],
                    name=scenario,
                    marker_color=colors.get(scenario),
                    mode="lines+markers", #only with scatter or line plot
                    line=dict(width=2,color=colors.get(scenario)),
                    )
            )

        fig.update_layout(
            title="Price by Period",
            xaxis_title="Period",
            yaxis_title="Price in US$",
            template="plotly_white",
            margin=dict(l=40, r=20, t=40, b=40),
            hovermode="x unified",
            showlegend=False
        )
        return fig
    
    def create_price_growth_plot(self, df: pd.DataFrame, colors:dict) -> go.Figure:
        fig = go.Figure()

        df["Price"] = np.where(
            df["quantity"] > 0,
            df["Value"] / df["quantity"],
            np.nan
        )

        df["Prev_Price"] = df.groupby("Scenario")["Price"].shift(1)
        df["Prev_Year"] = df.groupby("Scenario")["year"].shift(1)

        df["Year_Diff"] = df["year"] - df["Prev_Year"]

        df["Annual_Growth"] = (
            (df["Price"] / df["Prev_Price"]) ** (1 / df["Year_Diff"]) - 1
        ) * 100

        for scenario in df["Scenario"].unique():
            scenario_df = df[df["Scenario"] == scenario]

            fig.add_trace(
                go.Bar(
                    x=scenario_df["Period"],
                    y=scenario_df["Annual_Growth"],
                    name=scenario,
                    marker=dict(
                        color=colors.get(scenario)
                    )
                )
            )

        fig.update_layout(
            title="Price growth per year",
            yaxis_title="Growth in %",
            xaxis_title="Period",
            barmode="group",
            template="plotly_white",
            margin=dict(l=40, r=20, t=40, b=40),
            hovermode="x unified",
            showlegend=False
        )

        return fig

    def create_trade_line_plot(self, df: pd.DataFrame,
                               trade_domain:str,
                               unit:str,
                               colors:dict) -> go.Figure:
        df = df[df["domain"]==trade_domain]
        fig = go.Figure()
        plot_df = (
            df.groupby(["Scenario", "year"], as_index=False)[unit]
              .sum())

        for scenario in plot_df["Scenario"].unique():
            scenario_df = plot_df[plot_df["Scenario"] == scenario]
            fig.add_trace(
                go.Scatter(
                    x=scenario_df["year"],
                    y=scenario_df[unit],
                    name=scenario,
                    marker_color=colors.get(scenario),
                    mode="lines+markers", #only with scatter or line plot
                    line=dict(width=2,color=colors.get(scenario)),
                )
            )

        fig.update_layout(
            title=f"{trade_domain} {unit} per period",
            xaxis_title="year",
            yaxis_title=unit,
            template="plotly_white",
            margin=dict(l=40, r=20, t=40, b=40),
            hovermode="x unified",
            showlegend=False
        )       

        return fig
    
    def create_trade_bar_plot(self, df: pd.DataFrame,
                              trade_domain:str,
                              unit:str,
                              colors:dict) -> go.Figure:
        df = df[df["domain"]==trade_domain]
        fig = go.Figure()
        plot_df = (
            df.groupby(["Scenario", "Period"], as_index=False)[unit]
              .sum())

        for scenario in plot_df["Scenario"].unique():
            scenario_df = plot_df[plot_df["Scenario"] == scenario]
            if scenario == "Historic Data":
                pass
            else:
                fig.add_trace(
                    go.Bar(
                        x=scenario_df["Period"],
                        y=scenario_df[unit],
                        name=scenario,
                        marker=dict(
                            color=colors.get(scenario)
                        )
                    )
                )

        fig.update_layout(
            title=f"{trade_domain} {unit} per period",
            xaxis_title="Period",
            yaxis_title=unit,
            barmode="group",
            template="plotly_white",
            margin=dict(l=40, r=20, t=40, b=40),
            hovermode="x unified",
            showlegend=False
        )

        return fig

    def create_world_map_plot(self, 
                              filtered_data,
                              max_year,
                              ):
        country_data = filtered_data.groupby("ISO3")["quantity"].sum().reset_index()
        country_data = country_data[country_data["quantity"] >= 0.001]
        fig = px.choropleth(country_data, locations="ISO3", color="quantity",
                            hover_name="ISO3", color_continuous_scale="Greens")
        
        fig.update_layout(
            title=f"Worldmap for historic data in the year {max_year}",
            geo=dict(
                showcoastlines=True, 
                coastlinecolor="LightGray",
                projection_type="natural earth", 
                lonaxis_range=[-360,360], 
                lataxis_range=[-55,55]
            ),
            autosize=True,
            margin=dict(l=5, r=5, t=31, b=1),
            coloraxis_showscale=False
        )
        return fig

    def create_diff_world_map_plot(self, data, title: str):

        data = data.groupby("ISO3")["diff"].sum().reset_index()
        max_abs = max(abs(data["diff"].min()), abs(data["diff"].max()))

        color_scale = [
            (0.0, "red"),
            (0.5, "white"),
            (1.0, "green")
        ]

        fig = px.choropleth(
            data,
            locations="ISO3",
            color="diff",
            hover_name="ISO3",
            color_continuous_scale=color_scale,
            range_color=(-max_abs, max_abs)
        )

        fig.update_layout(
            title=f"{title}",
            title_x=0.5,
            geo=dict(
                showcoastlines=True,
                coastlinecolor="LightGray",
                projection_type="natural earth",
                lonaxis_range=[-360, 360],
                lataxis_range=[-55, 55],
            ),
            autosize=True,
            margin=dict(l=5, r=5, t=31, b=1),
            coloraxis_showscale=False,
            showlegend=False,
        )

        return fig

    def plot_forarea(self, df,colors:dict):
        periods = sorted(df["Period"].unique())

        fig = go.Figure()
        all_values = []
        for s in df["Scenario"].unique():
            area = df[df["Scenario"]==s].groupby("Period")["ForArea"].sum()
            area=area/1000
            y_vals = [area.get(p,0) for p in periods]
            all_values.extend(y_vals)

            fig.add_bar(
                x=periods, 
                y=y_vals, 
                marker_color=colors[s], 
                showlegend=False
            )

        fig.update_layout(
            title="Forest Area", 
            xaxis_title="Period", 
            yaxis_title="in million ha",
            barmode="group", 
            template=self.template, 
            yaxis=dict(range=PlotUtils.dynamic_y_range(all_values)),
            margin=dict(l=40, r=20, t=40, b=40),
        )
        return fig

    def plot_forstock(self, df:pd.DataFrame,colors:dict):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        all_values = []

        for s in df["Scenario"].unique():
            stock = df[df["Scenario"]==s].groupby("Period")["ForStock"].sum()
            y_vals = [stock.get(p,0) for p in periods]
            all_values.extend(y_vals)
            fig.add_bar(
                x=periods, 
                y=y_vals, 
                marker_color=colors[s], 
                showlegend=False
            )

        fig.update_layout(
            title="Forest Stock", 
            xaxis_title="Period", 
            yaxis_title="in million m³",
            barmode="group", 
            template=self.template, 
            yaxis=dict(range=PlotUtils.dynamic_y_range(all_values)),
            margin=dict(l=40, r=20, t=40, b=40),
        )
        return fig

    def plot_area_growth(self, df,colors:dict):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        for s in df["Scenario"].unique():
            df_s = df[df["Scenario"] == s]

            area = (
                df_s.groupby("Period")["ForArea"]
                .sum()
                .reindex(periods)
            )

            years = (
                df_s.groupby("Period")["year"]
                .mean()
                .reindex(periods)
            )

            delta_years = years.diff()

            area_change = (area / area.shift(1)) ** (1 / delta_years) - 1

            fig.add_scatter(
                x=periods, 
                y=area_change, 
                mode="lines+markers",
                line=dict(color=colors[s]), 
                showlegend=False
            )

        fig.update_layout(
            title="Annualized Forest Area Growth",
            xaxis_title="Period", 
            yaxis_title="Growth rate in %",
            yaxis_tickformat=".2%", 
            margin=dict(l=40, r=20, t=40, b=40),
            template=self.template
        )

        return fig

    def plot_stock_growth(self, df, colors: dict, calc: str):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        for s in df["Scenario"].unique():

            df_s = df[df["Scenario"] == s]

            agg = (
                df_s.groupby("Period")
                .agg({
                    "ForStock": "sum",
                    "supply_from_forest": "sum",
                    "year": "mean"
                })
                .reindex(periods)
            )

            delta_years = agg["year"].diff()
            stock = agg["ForStock"]

            nai = agg["ForStock"].diff() / delta_years

            if calc == "pct_change":
                stock_change = (stock / stock.shift(1)) ** (1 / delta_years) - 1
                title = "Annualized Forest Stock Growth"
                yaxis_title = "Growth rate in %"
                yaxis_tickformat = ".2%"

            elif calc == "sustainable_supply":
                stock_change = nai 
                title = "NAI minus total removals"
                yaxis_title = "in million m³"
                yaxis_tickformat = ".1f"

            else:
                stock_change = nai + (agg["supply_from_forest"]*1.2)
                title = "Net Annual Increment (NAI) per year"
                yaxis_title = "in million m³"
                yaxis_tickformat = ".1f"

            fig.add_scatter(
                x=periods,
                y=stock_change,
                mode="lines+markers",
                line=dict(color=colors[s]),
                showlegend=False,
            )

        fig.update_layout(
            title=title,
            xaxis_title="Period",
            yaxis_title=yaxis_title,
            yaxis_tickformat=yaxis_tickformat,
            template=self.template,
            margin=dict(l=40, r=20, t=40, b=40),
        )

        return fig

    def plot_stock_area_ratio(self, df,colors:dict):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        for s in df["Scenario"].unique():
            g = df[df["Scenario"]==s].groupby("Period")[["ForStock","ForArea"]].sum().replace(0,np.nan)
            ratio = g["ForStock"]/(g["ForArea"]/1000)

            fig.add_scatter(
                x=periods, 
                y=[ratio.get(p) for p in periods],
                mode="lines+markers", 
                line=dict(color=colors[s]), 
                showlegend=False
            )

        fig.update_layout(
            title="Forest density (Stock per Area)", 
            xaxis_title="Period", 
            yaxis_title="in 1 000 m³ per ha",
            template=self.template,
            margin=dict(l=40, r=20, t=40, b=40),
        )

        return fig

    def plot_supply_from_forest(self, df,colors:dict):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        for s in df["Scenario"].unique():
            sub = df[df["Scenario"]==s].sort_values("Period").groupby("Period")[["supply_from_forest","year"]].sum().reindex(periods)
            normalized_supply = sub["supply_from_forest"]
            supply_range = normalized_supply[normalized_supply > 0]

            fig.add_bar(
                x=periods, 
                y=normalized_supply, 
                marker_color=colors[s], 
                showlegend=False
            )

        fig.update_layout(
            title="Supply from Forest (per year change)", 
            xaxis_title="Period",
            yaxis_title="in million m³", 
            barmode="group", 
            template=self.template,
            yaxis=dict(range=PlotUtils.dynamic_y_range(supply_range)),
            margin=dict(l=40, r=20, t=40, b=40),
        )

        return fig
