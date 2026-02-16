from plotly.colors import qualitative
import pandas as pd
import numpy as np
from dash import dcc, html

class PlotUtils:
    
    @staticmethod
    def generate_color_palette(palette_name: str, n_colors: int):
        #palette_name = 'D3' #or, 'G10', 'T10', 'Alphabet', 'Dark24', etc.
        base_palette = getattr(qualitative, palette_name, qualitative.Plotly)
        return [base_palette[i % len(base_palette)] for i in range(n_colors)]

    @staticmethod
    def get_scenario_colors(scenarios, palette_name="D3"):
        n = len(scenarios)
        color_list = PlotUtils.generate_color_palette(palette_name, n)
        return {s: color_list[i % len(color_list)] for i, s in enumerate(scenarios)}

    @staticmethod
    def dynamic_y_range(values, lower_factor=0.9, upper_factor=1.1):
        values = np.array(values)
        values = values[~np.isnan(values)]
        if len(values) == 0:
            return None
        return [values.min() * lower_factor, values.max() * upper_factor]
    
    @staticmethod
    def filter_data(df:pd.DataFrame = None,region=None, 
                    continent=None, domain=None, commodity=None, 
                    commodity_group=None, scenario=None,year=None):
        filters = {
            "ISO3": region,
            "Continent": continent,
            "domain": domain,
            "Commodity": commodity,
            "Commodity_Group": commodity_group,
            "Scenario": scenario,
            "year": year,
        }

        for col, values in filters.items():
            if values is None or not values:
                continue
            if col in df.columns:
                df = df[df[col].isin(values)]
        return df
    
    @staticmethod
    def generate_title(region, continent, domain, commodity, commodity_group):
        parts = []
        for item in [region, continent, domain, commodity, commodity_group]:
            if item:
                parts.append(str(item))
        return ", ".join(parts).replace("[", "").replace("]", "").replace("'", "") or "all data"

    @staticmethod
    def remove_extreme_outliers(df, col, threshold=50):
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        limit = threshold * IQR
        df.loc[df[col] >= limit, col] = np.nan
        return df

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
            style={
                "display": "flex",
                "flexDirection": "column",
                "backgroundColor": "white",
                "border": "1px solid #e3e6ea",
                "borderRadius": "6px",
                "padding": "10px",
                "height": "100%", 
                "minHeight": "0",
            }
        )
