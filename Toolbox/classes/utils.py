from plotly.colors import qualitative
import pandas as pd
import numpy as np
from dash.dependencies import Input
from dash import dcc, html
from Toolbox.parameters.filter_config import PLOT_FILTERS

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
    def filter_data(df:pd.DataFrame = None,
                    region=None, 
                    continent=None, 
                    domain=None, 
                    commodity=None, 
                    commodity_group=None, 
                    scenario=None,
                    year=None,
                    ):
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
    def generate_title(filter_dict: dict, ignore_keys=None) -> str:
        ignore_keys = set(ignore_keys or [])

        parts = [
            str(v[0])
            for k, v in filter_dict.items()
            if k not in ignore_keys and v
        ]

        return ", ".join(parts) if parts else "sum of all data"

    @staticmethod
    def remove_extreme_outliers(df, col, threshold=50):
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        limit = threshold * IQR
        df.loc[df[col] >= limit, col] = np.nan
        return df

    @staticmethod    
    def build_filter_inputs(prefix, filter_config):
        return [
            Input(f"{prefix}_{key}-dropdown", "value")
            for key in filter_config.keys()
        ]

    @staticmethod
    def get_plot_filters(filter_values_dict, plot_name):
        return {
            k: filter_values_dict.get(k)
            for k in PLOT_FILTERS[plot_name]
        }