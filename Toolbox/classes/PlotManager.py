import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import textwrap
from Toolbox.classes.utils import PlotUtils
from Toolbox.parameters.default_parameters import under_to_over_bark
from Toolbox.classes.ring_plot_utils import RingPlotsUtils

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
            colors: dict,
            title: str,
            y_label:str
        ) -> go.Figure:

        # df = df[df["domain"] == trade_domain]

        fig = go.Figure()

        grouped = (
            df.groupby(["Scenario", "year"])[trade_domain]
            .sum()
            .unstack("Scenario")
            .sort_index()
        )

        y_label="million " + y_label
        for s in grouped.columns:
            y=grouped[s] / 1000
            
            # if unit=="Value":
            #     y_label="billion US$"
            #     y=grouped[s] / 1000000

            fig.add_scatter(
                x=grouped.index,
                y=y,
                mode="lines+markers",
                name=s,
                line=dict(width=2, color=colors.get(s)),
            )

        if title==None:
            title="Global"

        fig.update_layout(
            title={
                "text": f"Aggregated {trade_domain.split('_')[1]} quantity for <br>{title}",
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

        try:
            df = df[df["domain"] == trade_domain]
        except KeyError:
            pass

        try:
            df["Period"]
            time_var="Period"
        except KeyError:
            time_var="year"
        
        periods = sorted(df["year"].unique())

        fig = go.Figure()

        grouped = (
            df[df["Scenario"] != "Historic Data"]
            .groupby(["Scenario", time_var])[unit]
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

        if time_var=="Period":
            years_map = (
                df.groupby("Period")["year"]
                .max()
                .reindex(periods)
            )
        else:
            years_map=periods

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

    def create_trade_ring_plot(
        self,
        df: pd.DataFrame,
        trade_domain: str,
        unit: str,
        scenario: str,
        title: str,
        y_label: str,
        partner_col: str = "ISO3",
        top_n: int = 5,
        ring_unit: float | None = None,
        center_label: str | None = None,
        partner_colors: dict | None = None,
        row_label: str = "Rest of World",
        row_outermost: bool = True,
        forecast_is_dark: bool = True,
    ) -> go.Figure:
        """
        Ring plot of the trade partners over the years (one segment per year).

        The call is similar to create_trade_bar_plot, but a ring plot shows ONE
        scenario, so `scenario` is passed instead of the scenario `colors`.
        The colours are assigned per partner (see RING_PALETTE).

        How to read it
        --------------
        - One segment (equal angle) per year. The segment is divided into rings
            of fixed thickness `ring_unit`, so the number of rings shows the total
            trade of the year.
        - Partners are filled into the rings from the inside to the outside:
            the LARGEST partner is closest to the centre, the SMALLEST is on the
            outside. A partner that needs more than one ring continues in the
            next ring, so its share is the width of its elements.
        - "Rest of world" (all partners outside the top N) is the outermost
            element by default (`row_outermost`).
        - Years up to the last "Historic Data" year use one tone of a partner's
            colour, forecast years of `scenario` use the other tone.
        - Separator lines appear only where two different partners touch.

        Parameters
        ----------
        df               Trade data with the columns domain, Scenario, year,
                            `partner_col` and `unit`.
        trade_domain     Value of the "domain" column to plot (e.g. "Export").
        unit             "Value" or "quantity" (same conversion as in the
                            other trade plots).
        scenario         Scenario that is shown for the forecast years.
        title            Plot title (second line, like the other plots).
        y_label          Unit name used for quantities, e.g. "m3".
        partner_col      Column with the partner country.
        top_n            Number of partners that get their own colour; all
                            others are summed into `row_label`.
        ring_unit        Value (after unit conversion) represented by one ring.
                            None = chosen automatically, so that the largest year
                            has about 15 rings.
        center_label     Text in the centre hole, e.g. "DEU" (None = no text).
        partner_colors   Optional {partner: (dark, light)} to override colours.
        row_outermost    True: "rest of world" is always outermost.
                            False: it is sorted by size like any other partner.
        forecast_is_dark True: forecast = dark tone, history = light tone.
        """
        rpu = RingPlotsUtils()
        df = df[df["domain"] == trade_domain]
        if df.empty:
            return rpu._ring_empty_figure(f"No data for {trade_domain}")

        # Historic years come from "Historic Data", later years from `scenario`
        hist = df[df["Scenario"] == "Historic Data"]
        last_actual = int(hist["year"].max()) if not hist.empty else int(df["year"].min()) - 1
        forecast = df[(df["Scenario"] == scenario) & (df["year"] > last_actual)]
        data = pd.concat([hist, forecast])

        if data.empty:
            return rpu._ring_empty_figure(f"No data for {trade_domain} / {scenario}")

        # Same unit conversion as in create_trade_line_plot / create_trade_bar_plot
        if unit == "Value":
            factor, unit_label = 1 / 1000000, "billion US$"
        else:
            factor, unit_label = 1 / 1000, "million " + y_label

        data = data.groupby(["year", partner_col], as_index=False)[unit].sum()
        data[unit] = data[unit] * factor

        pivot, top = rpu._ring_aggregate_partners(data, "year", partner_col, unit, top_n, row_label)
        cmap = rpu._ring_assign_colors(top, row_label, partner_colors)

        if ring_unit is None:
            ring_unit = rpu._ring_nice_unit(float(pivot.sum(axis=1).max()))

        geo = rpu._ring_compute_geometry(pivot, top, last_actual, ring_unit, 2.0, row_label, row_outermost)

        fig = go.Figure()
        for trace in rpu._ring_area_traces(geo, top, row_label, cmap, unit_label, forecast_is_dark):
            fig.add_trace(trace)
        fig.add_trace(rpu._ring_separator_trace(geo, "white"))
        fig.add_trace(rpu._ring_total_trace(geo))

        rpu._ring_apply_layout(
            fig, geo, ring_unit, unit_label, 0.12, center_label, 14,
            f"{trade_domain} {unit} by partner for <br>{title}",
        )
        return fig
