import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import textwrap
from Toolbox.classes.utils import PlotUtils
from Toolbox.parameters.default_parameters import under_to_over_bark

class Plots:

    def __init__(self, template="plotly_white"):
        self.template = template
        self.pad_down = 150
        self.margin_top = 60
        self.title_x = 0.5
        self.title_y = 0.925

    def create_quantity_plot(
            self, 
            df: pd.DataFrame,
            colors: dict,
            title: str,
            y_label:str,
        ):
        
        grouped_df = df.groupby(["year", "Scenario"]).sum().reset_index()

        fig = go.Figure()
        for i, scenario in enumerate(grouped_df["Scenario"].unique()):
            subset = grouped_df[grouped_df["Scenario"] == scenario]
            dash = "solid" if scenario == "Historic Data" else "dash"
            fig.add_trace(
                go.Scatter(
                    x=subset["year"], 
                    y=subset["quantity"] / 1000,
                    mode="lines", 
                    name=scenario,
                    line=dict(color=colors.get(scenario), 
                    )
                )
            )

        fig.update_layout(
            showlegend=False,
            title={
                "text": f"Quantity for <br>{title}",
                "x": self.title_x,
                "y": 0.96,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                title="Year", 
            ),
            yaxis=dict(
                title=f"Quantity in million {y_label}", 
                rangemode="nonnegative",
            ),
            hovermode="x unified",
            template=self.template,
            autosize = True,
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
        )
        return fig

    def create_value_plot(
            self, 
            df: pd.DataFrame, 
            colors: dict, 
            title: str
        ) -> go.Figure:

        periods = sorted(df["Period"].unique())

        fig = go.Figure()

        grouped = (
            df.groupby(["Scenario", "Period"])["Value"]
            .sum()
            .unstack("Scenario")
            .reindex(periods)
        )

        all_values = grouped.replace(0, np.nan).values.flatten() 

        for s in grouped.columns:
            if s == "Historic Data":
                pass
            else:
                fig.add_scatter(
                    x=periods,
                    y=grouped[s] / 1000000,
                    mode="lines+markers",
                    name=s,
                    line=dict(width=2, color=colors.get(s)),
                )

        years_map = df.groupby("Period")["year"].max().reindex(periods)

        fig.update_layout(
            title={
                "text": f"Value for <br>{title}",
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=years_map,
                title="Year"
            ),
            yaxis=dict(
                title="in billion US$",
                range=PlotUtils.dynamic_y_range(all_values / 1000000)
            ),
            template="plotly_white",
            barmode="group",
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
            hovermode="x unified",
            showlegend=False,
        )

        return fig
    
    def create_value_growth_plot(
            self, 
            df: pd.DataFrame, 
            colors: dict, 
            title: str
        ) -> go.Figure:

        periods = sorted(df["Period"].unique())

        fig = go.Figure()

        grouped = (
            df.groupby(["Scenario", "Period"])
            .agg({"Value": "sum", "year": "mean"})
            .unstack("Scenario")
            .reindex(periods)
        )

        delta_years = grouped["year"].diff().replace(0, np.nan)

        for s in grouped["Value"].columns:
            if s == "Historic Data":
                pass
            else:
                value = grouped["Value"][s]
                growth = (value / value.shift(1)) ** (1 / delta_years[s]) - 1

                fig.add_bar(
                    x=periods,
                    y=growth,
                    name=s,
                    marker_color=colors.get(s),
                )

        years_map = df.groupby("Period")["year"].max().reindex(periods)

        fig.update_layout(
            title={
                "text": f"Growth in value for <br>{title}",
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=years_map,
                title="Year"
            ),
            yaxis=dict(
                title="Growth in %",
            ),
            yaxis_tickformat=".1%",
            template="plotly_white",
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
            hovermode="x unified",
            showlegend=False
        )

        return fig

    def create_price_plot(
            self, 
            df: pd.DataFrame, 
            colors: dict, 
            title: str
        ) -> go.Figure:

        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        grouped = (
            df.groupby(["Scenario", "Period"])
            .agg({
                "Value": "sum",
                "quantity": "sum",
                "year": "mean"
            })
            .reindex(pd.MultiIndex.from_product(
                [df["Scenario"].unique(), periods],
                names=["Scenario", "Period"]
            ))
        )

        grouped["Price"] = grouped["Value"] / grouped["quantity"].replace(0, np.nan)

        price_df = PlotUtils.remove_extreme_outliers(grouped, "Price")
        all_values = price_df["Price"].replace(0, np.nan).values.flatten()

        price_table = grouped["Price"].unstack("Scenario")

        for s in price_table.columns:
            if s == "Historic Data":
                pass
            else:
                fig.add_scatter(
                    x=periods,
                    y=price_table[s],
                    mode="lines+markers",
                    name=s,
                    line=dict(width=2, color=colors.get(s)),
                )

        years_map = (df.groupby("Period")["year"].max().reindex(periods))

        fig.update_layout(
            title={
                "text": f"Price (unit value) for <br>{title}",
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=years_map,
                title="Year"
            ),
            yaxis=dict(
                title="Unit Value in US$",
                range=PlotUtils.dynamic_y_range(all_values),
            ),
            template="plotly_white",
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
            hovermode="x unified",
            showlegend=False
        )

        return fig
    
    def create_price_growth_plot(
            self, 
            df: pd.DataFrame, 
            colors: dict,
            title: str,
        ) -> go.Figure:

        periods = sorted(df["Period"].unique())

        fig = go.Figure()

        grouped = (
            df.groupby(["Scenario", "Period"])
            .agg({
                "Value": "sum",
                "quantity": "sum",
                "year": "mean"
            })
            .unstack("Scenario")
            .reindex(periods)
        )

        price = grouped["Value"] / grouped["quantity"].replace(0, np.nan)

        delta_years = grouped["year"].diff().replace(0, np.nan)

        for s in price.columns:
            if s == "Historic Data":
                pass
            else:
                p = price[s]
                growth = (p / p.shift(1)) ** (1 / delta_years[s]) - 1

                fig.add_bar(
                    x=periods,
                    y=growth,
                    name=s,
                    marker_color=colors.get(s),
                )

        years_map = df.groupby("Period")["year"].max().reindex(periods)

        fig.update_layout(
            title={
                "text": f"Annual price growth for <br>{title}",
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            yaxis_title="Growth in %",
            yaxis_tickformat=".1%",
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=years_map,
                title="Year"
            ),
            barmode="group",
            template="plotly_white",
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
            hovermode="x unified",
            showlegend=False
        )

        return fig
    
    def create_trade_line_plot(
            self, 
            df: pd.DataFrame,
            trade_domain: str,
            unit: str,
            colors: dict,
            title: str,
            y_label:str
        ) -> go.Figure:

        df = df[df["domain"] == trade_domain]

        fig = go.Figure()

        grouped = (
            df.groupby(["Scenario", "year"])[unit]
            .sum()
            .unstack("Scenario")
            .sort_index()
        )

        y_label="million " + y_label
        for s in grouped.columns:
            y=grouped[s] / 1000
            
            if unit=="Value":
                y_label="billion US$"
                y=grouped[s] / 1000000

            fig.add_scatter(
                x=grouped.index,
                y=y,
                mode="lines+markers",
                name=s,
                line=dict(width=2, color=colors.get(s)),
            )

        fig.update_layout(
            title={
                "text": f"{trade_domain} {unit} for <br>{title}",
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(title="Year"),
            yaxis_title=f"{trade_domain} in {y_label}",
            template="plotly_white",
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
            hovermode="x unified",
            showlegend=False,
        )

        return fig
    
    def create_trade_bar_plot(
            self,
            df: pd.DataFrame,
            trade_domain: str,
            unit: str,
            colors: dict,
            title: str,
            y_label: str,
        ) -> go.Figure:

        df = df[df["domain"] == trade_domain]

        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        grouped = (
            df[df["Scenario"] != "Historic Data"]
            .groupby(["Scenario", "Period"])[unit]
            .sum()
            .unstack("Scenario")
            .reindex(periods)
        )

        y_label="million " + y_label
        for s in grouped.columns:
            y=grouped[s] / 1000
            
            if unit=="Value":
                y_label="billion US$"
                y=grouped[s] / 1000000

            fig.add_bar(
                x=periods,
                y=y,
                name=s,
                marker_color=colors.get(s)
            )

        years_map = (
            df.groupby("Period")["year"]
            .max()
            .reindex(periods)
        )

        fig.update_layout(
            title={
                "text": f"{trade_domain} for<br>{title}",
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=years_map,
                title="Year"
            ),
            yaxis_title=f"{trade_domain} in {y_label}",
            barmode="group",
            template="plotly_white",
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
            hovermode="x unified",
            showlegend=False,
        )

        return fig

    def create_world_map_plot(self, 
                              filtered_data:pd.DataFrame,
                              max_year,
                              title: str,
                              colorbar_label:str
                              ):
        
        country_data = filtered_data.groupby("ISO3")["quantity"].sum().reset_index()
        country_data = country_data[country_data["quantity"] >= 0.001]
        country_data["quantity"] = country_data["quantity"] / 1000

        fig = px.choropleth(country_data, locations="ISO3", color="quantity",
                            hover_name="ISO3", color_continuous_scale="Greens")
        
        fig.update_layout(
            title={
                "text": f"Historic data in {max_year} for<br>{title}",
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                #"pad": {"b": self.pad_down}
            },
            geo=dict(
                showcoastlines=True, 
                coastlinecolor="LightGray",
                projection_type="natural earth", 
                lonaxis_range=[-360,360], 
                lataxis_range=[-55,55]
            ),
            autosize=True,
            margin=dict(l=5, r=5, t=self.margin_top, b=1),
            coloraxis_showscale=True,
            coloraxis=dict(
                colorbar=dict(
                    title=dict(
                        text=f"Quantity<br>in million<br>{colorbar_label}",
                        font=dict(size=10)
                    ),
                    tickfont=dict(size=10),
                    tickformat=".2s",
                    thickness=10,
                )
            )
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
            title_x=self.title_x,
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

    def plot_forarea(
            self,
            df,
            colors:dict,
            title:str,
        ):

        periods = sorted(df["Period"].unique())

        fig = go.Figure()

        grouped = (
            df.groupby(["Scenario", "Period"])["ForArea"]
            .sum()
            .div(1000)
            .unstack("Scenario")
        )

        all_values = grouped.fillna(0).values.flatten()

        for s in grouped.columns:
            y_vals = grouped[s].reindex(periods, fill_value=0)

            fig.add_bar(
                x=periods,
                y=y_vals,
                marker_color=colors[s],
                name=s,
                showlegend=False
            )

            year_map = (
                df.groupby("Period")["year"]
                .mean()
                .reindex(periods)
            )

        fig.update_layout(
            title={
                "text": f"Forest Area for <br>{title}", 
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=year_map, 
                title="Year"
            ),  
            yaxis_title="in million ha",
            barmode="group", 
            template=self.template, 
            yaxis=dict(range=PlotUtils.dynamic_y_range(all_values)),
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
        )
        return fig

    def plot_forstock(self, 
                      df:pd.DataFrame,
                      colors:dict,
                      title:str,
        ):
        periods = sorted(df["Period"].unique())
        fig = go.Figure()
        
        grouped = (
            df.groupby(["Scenario", "Period"])["ForStock"]
            .sum()
            .unstack("Scenario")
        )

        all_values = grouped.fillna(0).values.flatten()

        for s in grouped.columns:
            y_vals = grouped[s].reindex(periods, fill_value=0)

            fig.add_bar(
                x=periods,
                y=y_vals,
                marker_color=colors[s],
                name=s,
                showlegend=False
            )

            year_map = (
                df.groupby("Period")["year"]
                .mean()
                .reindex(periods)
            )

        fig.update_layout(
            title={
                "text": f"Forest Stock for <br>{title}", 
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=year_map, 
                title="Year"
            ), 
            yaxis_title="in million m³",
            barmode="group", 
            template=self.template, 
            yaxis=dict(range=PlotUtils.dynamic_y_range(all_values)),
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
        )
        return fig

    def plot_forest_growth(
            self, 
            df, 
            colors: dict, 
            title: str,
            domain:list,
        ):

        if domain=="ForStock":
            domain_name = "Stock"
        else:
            domain_name = "Area"

        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        grouped_area = (
            df.groupby(["Scenario", "Period"])[domain]
            .sum()
            .unstack("Scenario")
            .reindex(periods)
        )

        grouped_years = (
            df.groupby(["Scenario", "Period"])["year"]
            .mean()
            .unstack("Scenario")
            .reindex(periods)
        )

        delta_years = grouped_years.diff().replace(0, np.nan)

        for s in grouped_area.columns:
            area_change = (grouped_area[s] / grouped_area[s].shift(1)) ** (1 / delta_years[s]) - 1

            fig.add_scatter(
                x=periods,
                y=area_change,
                mode="lines+markers",
                line=dict(color=colors[s]),
                name=s,
                showlegend=False
            )

        years_map = df.groupby("Period")["year"].mean().reindex(periods)

        fig.update_layout(
            title={
                "text": f"Annual Forest {domain_name} Growth for<br>{title}",
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=years_map,
                title="Year"
            ),
            yaxis_title="Growth rate in %",
            yaxis_tickformat=".3%",
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
            template=self.template
        )

        return fig

    def plot_nai(
            self, 
            df, 
            colors: dict, 
            calc: str, 
            title: str
        ):

        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        grouped = (
            df.groupby(["Scenario", "Period"])
            .agg({"ForStock": "sum", "supply_from_forest": "sum", "year": "mean"})
            .unstack("Scenario")
            .reindex(periods)
        )

        delta_years = grouped['year'].diff().replace(0, np.nan)

        for s in grouped['ForStock'].columns:
            stock = grouped['ForStock'][s]
            supply = grouped['supply_from_forest'][s]

            nai_without_removals = stock.diff()# / delta_years[s]
            supply_ob = (supply * under_to_over_bark)
            nai = nai_without_removals + supply_ob / delta_years[s]

            if calc == "sustainable_supply":
                value = supply_ob  / delta_years[s] / nai.replace(0, np.nan)
                yaxis_title = "in %"
                yaxis_tickformat = ".1%"
                plot_title = f"Total Removals as a Share of NAI for<br>{title}"
            else:
                value = nai
                yaxis_title = "in million m³"
                yaxis_tickformat = ".1f"
                plot_title = f"Net Annual Increment (NAI, over bark) for<br>{title}"

            fig.add_scatter(
                x=periods,
                y=value,
                mode="lines+markers",
                line=dict(color=colors[s]),
                name=s,
                showlegend=False
            )

        years_map = df.groupby("Period")["year"].mean().reindex(periods)

        fig.update_layout(
            title={
                "text": plot_title,
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=years_map,
                title="Year"
            ),
            yaxis_title=yaxis_title,
            yaxis_tickformat=yaxis_tickformat,
            template=self.template,
            margin=dict(l=40, r=20, t=self.margin_top, b=40)
        )

        return fig

    def plot_stock_area_ratio(
            self, 
            df, 
            colors: dict, 
            title: str
        ):

        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        grouped = (
            df.groupby(["Scenario", "Period"])[["ForStock", "ForArea"]]
            .sum()
            .replace(0, np.nan)
            .unstack("Scenario")
            .reindex(periods)
        )

        for s in grouped["ForStock"].columns:
            stock = grouped["ForStock"][s]
            area = grouped["ForArea"][s]
            ratio = stock / (area / 1000)

            fig.add_scatter(
                x=periods,
                y=ratio,
                mode="lines+markers",
                line=dict(color=colors[s]),
                #name=s,
                showlegend=False
            )

        years_map = df.groupby("Period")["year"].mean().reindex(periods)

        fig.update_layout(
            title={
                "text": f"Forest density (Stock per Area) for<br>{title}",
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=years_map,
                title="Year"
            ),
            yaxis_title="in m³ per ha",
            template=self.template,
            margin=dict(l=40, r=20, t=self.margin_top, b=40)
        )

        return fig

    def plot_supply_from_forest(
            self,
            df,
            colors:dict,
            title:str,
        ):

        periods = sorted(df["Period"].unique())
        fig = go.Figure()

        grouped = (
            df.groupby(["Scenario", "Period"])["supply_from_forest"]
            .sum()
            .unstack("Scenario")
        )

        years = (df.groupby(["Period"])["year"].mean())
        delta_years = years.diff().replace(0, np.nan)

        for s in grouped.columns:
            y_vals = (
                grouped[s].reindex(periods, fill_value=0) * 
                under_to_over_bark /
                delta_years
            )

            fig.add_bar(
                x=periods,
                y=y_vals,
                marker_color=colors[s],
                name=s,
                showlegend=False
            )

            year_map = (
                df.groupby("Period")["year"]
                .mean()
                .reindex(periods)
            )

        fig.update_layout(
            title={
                "text": f"Total removals (over bark, per year change) for<br>{title}", 
                "x": self.title_x,
                "y": self.title_y,
                "xanchor": "center",
                "pad": {"b": self.pad_down}
            },
            xaxis=dict(
                tickmode="array",
                tickvals=periods,
                ticktext=year_map, 
                title="Year"
            ), 
            yaxis_title="in million m³", 
            barmode="group", 
            template=self.template,
            yaxis=dict(range=PlotUtils.dynamic_y_range(y_vals)),
            margin=dict(l=40, r=20, t=self.margin_top, b=40),
        )

        return fig
