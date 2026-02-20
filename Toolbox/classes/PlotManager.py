import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import textwrap
from Toolbox.classes.utils import PlotUtils

class Plots:

    def __init__(self, template="plotly_white"):
        self.template = template

    def create_quantity_plot(self, df,# start_year, end_year, plot_settings, title_suffix
                             ):
        grouped_df = df.groupby(["year", "Scenario"]).sum().reset_index()
        #grouped_df = grouped_df[(grouped_df["year"] >= start_year) & (grouped_df["year"] <= end_year)]
        colors = PlotUtils.get_scenario_colors(scenarios=grouped_df["Scenario"].unique())

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
                              #dash=dash, width=plot_settings["line_witdh"]
                    )
                )
            )

        title = f"Quantity by Year and Scenario for"# {title_suffix}"
        fig.update_layout(
            showlegend=False,
            title=dict(
                text="<br>".join(textwrap.wrap(title, 90)),
                #font=dict(size=plot_settings["title_font_size"])
            ),
            xaxis=dict(
                title="Year", 
                #tickfont=dict(size=plot_settings["tick_font_size"])
            ),
            yaxis=dict(
                title="Quantity", 
                rangemode="nonnegative",
                #tickfont=dict(size=plot_settings["tick_font_size"])
            ),
            # legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center",
            #             font=dict(size=plot_settings["legend_font_size"])),
            hovermode="x unified",
            template=self.template,
            autosize = True,
            margin=dict(l=40, r=20, t=40, b=40),
        )
        return fig

    def create_value_plot(self, df: pd.DataFrame) -> go.Figure:
        df["Value"] = df.price * df.quantity
        fig = go.Figure()
        plot_df = (
            df.groupby(["Scenario", "Period"], as_index=False)["Value"]
              .sum())

        try:
            colors = PlotUtils().get_scenario_colors(
                plot_df["Scenario"].unique())
        except Exception:
            colors = {}

        for scenario in plot_df["Scenario"].unique():
            scenario_df = plot_df[plot_df["Scenario"] == scenario]

            fig.add_trace(
                go.Bar(
                    x=scenario_df["Period"],
                    y=scenario_df["Value"],
                    #mode="lines+markers", #only with scatter or line plot
                    name=scenario,
                    marker=dict(color=colors.get(scenario)),
                    # line=dict(
                    #     width=2,
                    #     color=colors.get(scenario)
                    # )
                )
            )

        fig.update_layout(
            title="Total Value over Time",
            xaxis_title="Period",
            yaxis_title="Value",
            template="plotly_white",
            barmode="group",
            margin=dict(l=40, r=20, t=40, b=40),
            hovermode="x unified",
            showlegend=False
        )

        return fig
    
    def create_value_growth_plot(self, df: pd.DataFrame) -> go.Figure:
        fig = go.Figure()
        agg_df = (
            df.groupby(["Scenario", "Period", "year"], as_index=False)
            .agg({
                "Value": "sum",
                "quantity": "sum"
            })
        )

        agg_df["Prev_Value"] = agg_df.groupby("Scenario")["Value"].shift(1)
        agg_df["Prev_Year"] = agg_df.groupby("Scenario")["year"].shift(1)

        agg_df["Year_Diff"] = agg_df["year"] - agg_df["Prev_Year"]

        agg_df["Annual_Growth"] = (
            (agg_df["Value"] / agg_df["Prev_Value"]) ** (1 / agg_df["Year_Diff"]) - 1
        ) * 100

        try:
            colors = PlotUtils().get_scenario_colors(
                agg_df["Scenario"].unique()
            )
        except Exception:
            colors = {}

        for scenario in agg_df["Scenario"].unique():
            scenario_df = agg_df[agg_df["Scenario"] == scenario]

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
            title="Value growth per year in %",
            xaxis_title="Period",
            yaxis_title="Growth (%)",
            template="plotly_white",
            margin=dict(l=40, r=20, t=40, b=40),
            hovermode="x unified",
            showlegend=False
        )

        return fig

    def create_price_plot(self, df: pd.DataFrame) -> go.Figure:
        fig = go.Figure()
        agg_df = (
            df.groupby(["Scenario", "Period"], as_index=False)
              .agg({
                  "Value": "sum",
                  "quantity": "sum"
              })
        )
        agg_df["Price"] = np.where(
            agg_df["quantity"] > 0,
            agg_df["Value"] / agg_df["quantity"],
            np.nan
        )

        try:
            colors = PlotUtils().get_scenario_colors(
                agg_df["Scenario"].unique()
            )
        except Exception:
            colors = {}

        for scenario in agg_df["Scenario"].unique():
            scenario_df = agg_df[agg_df["Scenario"] == scenario]

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
            yaxis_title="Price",
            template="plotly_white",
            margin=dict(l=40, r=20, t=40, b=40),
            hovermode="x unified",
            showlegend=False
        )
        return fig
    
    def create_price_growth_plot(self, df: pd.DataFrame) -> go.Figure:
        df = df.copy()

        fig = go.Figure()
        agg_df = (
            df.groupby(["Scenario", "Period", "year"], as_index=False)
            .agg({
                "Value": "sum",
                "quantity": "sum"
            })
        )

        agg_df["Price"] = np.where(
            agg_df["quantity"] > 0,
            agg_df["Value"] / agg_df["quantity"],
            np.nan
        )

        agg_df["Prev_Price"] = agg_df.groupby("Scenario")["Price"].shift(1)
        agg_df["Prev_Year"] = agg_df.groupby("Scenario")["year"].shift(1)

        agg_df["Year_Diff"] = agg_df["year"] - agg_df["Prev_Year"]

        agg_df["Annual_Growth"] = (
            (agg_df["Price"] / agg_df["Prev_Price"]) ** (1 / agg_df["Year_Diff"]) - 1
        ) * 100

        try:
            colors = PlotUtils().get_scenario_colors(
                agg_df["Scenario"].unique()
            )
        except Exception:
            colors = {}

        for scenario in agg_df["Scenario"].unique():
            scenario_df = agg_df[agg_df["Scenario"] == scenario]

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
            title="Price growth per year in %",
            yaxis_title="Growth (%)",
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
                               unit:str) -> go.Figure:
        df = df[df["domain"]==trade_domain]
        fig = go.Figure()
        plot_df = (
            df.groupby(["Scenario", "year"], as_index=False)[unit]
              .sum())

        try:
            colors = PlotUtils().get_scenario_colors(
                plot_df["Scenario"].unique())
        except Exception:
            colors = {}

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
                                       unit:str) -> go.Figure:
        df = df[df["domain"]==trade_domain]
        fig = go.Figure()
        plot_df = (
            df.groupby(["Scenario", "Period"], as_index=False)[unit]
              .sum())

        try:
            colors = PlotUtils().get_scenario_colors(
                plot_df["Scenario"].unique())
        except Exception:
            colors = {}

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

    def create_diff_world_map_plot(self, 
                                  data,
                                  max_year,
                                  title:str,
                                  ):
        
        data = data.groupby("ISO3")["diff"].sum().reset_index()
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
            range_color=(data["diff"].min(), data["diff"].max())
        )

        fig.update_layout(
            title=f"{title} in the year {max_year}",
            geo=dict(
                showcoastlines=True, 
                coastlinecolor="LightGray",
                projection_type="natural earth", 
                lonaxis_range=[-360,360], 
                lataxis_range=[-55,55],
            ),
            autosize=True,
            margin=dict(l=5, r=5, t=31, b=1),
            coloraxis_showscale=False,
            showlegend=False,
        )

        return fig

    def plot_forarea(self, df):
        periods = sorted(df["Period"].unique())
        
        try:
            colors = PlotUtils().get_scenario_colors(
                df["Scenario"].unique())
        except Exception:
            colors = {}

        fig = go.Figure()
        all_values = []
        for s in df["Scenario"].unique():
            area = df[df["Scenario"]==s].groupby("Period")["ForArea"].sum()
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
            yaxis_title="Sum of ForArea",
            barmode="group", 
            template=self.template, 
            yaxis=dict(range=PlotUtils.dynamic_y_range(all_values)),
            margin=dict(l=40, r=20, t=40, b=40),
        )
        return fig

    def plot_forstock(self, df):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        all_values = []
        
        try:
            colors = PlotUtils().get_scenario_colors(
                df["Scenario"].unique())
        except Exception:
            colors = {}

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
            yaxis_title="Sum of ForStock",
            barmode="group", 
            template=self.template, 
            yaxis=dict(range=PlotUtils.dynamic_y_range(all_values)),
            margin=dict(l=40, r=20, t=40, b=40),
        )
        return fig

    def plot_area_growth(self, df):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        
        try:
            colors = PlotUtils().get_scenario_colors(
                df["Scenario"].unique())
        except Exception:
            colors = {}

        for s in df["Scenario"].unique():
            area = df[df["Scenario"]==s].groupby("Period")["ForArea"].sum().reindex(periods)
            fig.add_scatter(
                x=periods, 
                y=area.pct_change(), 
                mode="lines+markers",
                line=dict(color=colors[s]), 
                showlegend=False
            )

        fig.update_layout(
            title="Forest Area Growth",
            xaxis_title="Period", 
            yaxis_title="Growth rate",
            yaxis_tickformat=".1%", 
            margin=dict(l=40, r=20, t=40, b=40),
            template=self.template
        )

        return fig

    def plot_stock_growth(self, df):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        
        try:
            colors = PlotUtils().get_scenario_colors(
                df["Scenario"].unique())
        except Exception:
            colors = {}

        for s in df["Scenario"].unique():
            stock = df[df["Scenario"]==s].groupby("Period")["ForStock"].sum().reindex(periods)
            fig.add_scatter(
                x=periods, 
                y=stock.pct_change(), 
                mode="lines+markers",
                line=dict(color=colors[s]), 
                showlegend=False
            )

        fig.update_layout(
            title="Forest Stock Growth",
            xaxis_title="Period", 
            yaxis_title="Growth rate",
            yaxis_tickformat=".1%", 
            template=self.template,
            margin=dict(l=40, r=20, t=40, b=40),
        )

        return fig

    def plot_stock_area_ratio(self, df):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        try:
            colors = PlotUtils().get_scenario_colors(
                df["Scenario"].unique())
        except Exception:
            colors = {}

        for s in df["Scenario"].unique():
            g = df[df["Scenario"]==s].groupby("Period")[["ForStock","ForArea"]].sum().replace(0,np.nan)
            ratio = g["ForStock"]/g["ForArea"]

            fig.add_scatter(
                x=periods, 
                y=[ratio.get(p) for p in periods],
                mode="lines+markers", 
                line=dict(color=colors[s]), 
                showlegend=False
            )

        fig.update_layout(
            title="Stock / Area", 
            xaxis_title="Period", 
            yaxis_title="Stock per Area",
            template=self.template,
            margin=dict(l=40, r=20, t=40, b=40),
        )

        return fig

    def plot_supply_from_forest(self, df):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        
        try:
            colors = PlotUtils().get_scenario_colors(
                df["Scenario"].unique())
        except Exception:
            colors = {}

        for s in df["Scenario"].unique():
            sub = df[df["Scenario"]==s].sort_values("Period").groupby("Period")[["supply_from_forest","year"]].sum().reindex(periods)
            delta_year = sub["year"].diff()
            normalized_supply = sub["supply_from_forest"]/delta_year

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
            template=self.template,
            margin=dict(l=40, r=20, t=40, b=40),
        )

        return fig
