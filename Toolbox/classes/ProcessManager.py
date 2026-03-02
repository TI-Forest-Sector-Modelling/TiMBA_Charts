import pickle
import pandas as pd
from pathlib import Path
import os
import pickle
import gzip
import os
import Toolbox.parameters.default_parameters as dp

class DataProcessor:
    def __init__(self, data, country_data,commodity_data,data_hist):
        self.data = data
        self.country_data = country_data
        self.commodity_data = commodity_data
        self.data_hist = data_hist

    def combined_data(self):
        """
        combine data imports
        """
        self.forest_data = self.data[dp.forest_db]
        self.data[dp.forest_formip_db] = self.data[dp.forest_db] 

        self.forest_data = self.forest_data[[
            'Scenario',
            'RegionCode',
            'Period',
            'ForStock',
            'ForArea',
            'supply_from_forest'
            ]
        ]
        
        self.forest_data = self.forest_data.drop_duplicates(
            subset=[
                'Scenario', 
                'RegionCode',
                'Period'
                ], 
            keep='first'
            )
        
        year_df= self.data[dp.overview_db][["Period","year"]].drop_duplicates()
        year_dict = dict(
            zip(
                year_df["Period"],
                year_df["year"]
                )
            )
        
        country_dict = dict(
            zip(
                self.country_data["RegionCode"], 
                self.country_data["ISO3"]
                )
            )

        continent_dict = dict(
            zip(
                self.country_data["RegionCode"], 
                self.country_data["Continent"]
                )
            )

        self.data[dp.overview_db] = pd.concat(
            [
                self.data[dp.overview_db], 
                self.data_hist
            ], 
            axis=0
            )
        
        self.data[dp.overview_db] = pd.merge(
            self.data[dp.overview_db], 
            self.country_data, 
            on="RegionCode", 
            how="left"
            )
        
        self.data[dp.overview_db] = pd.merge(
            self.data[dp.overview_db], 
            self.commodity_data, 
            on="CommodityCode", 
            how="left"
            )

        self.data[dp.overview_db]["domain"] = self.data[dp.overview_db]["domain"].replace({
            'ManufactureCost': 'Manufacturing',
            'TransportationExport': 'Export',
            'TransportationImport': 'Import',
            }
        )
        
        self.data[dp.overview_db]["Value"] = (
            self.data[dp.overview_db].price * 
            self.data[dp.overview_db].quantity
            )

        self.data[dp.overview_db] = self.data[dp.overview_db][[
            'Model',
            'Scenario',
            'RegionCode',
            'Continent',
            'Country',
            'ISO3',
            'CommodityCode',
            'Commodity',
            'Commodity_Group',
            'Unit',
            'Period',
            'year',
            'domain',
            'price',
            'quantity',
            'Value',
            ]
        ]
        
        self.forest_data["ISO3"] = self.forest_data["RegionCode"].map(country_dict)
        self.forest_data["Continent"] = self.forest_data["RegionCode"].map(continent_dict)
        self.forest_data["year"] = self.forest_data["Period"].map(year_dict)
        self.data[dp.forest_db] = self.forest_data
        
        return self.data

    def pivot_map_data(self):
        df = self.data[dp.overview_db]
        cols = [
            "Continent",
            "ISO3",
            "Scenario",
            "domain",
            "year",
            "Commodity",
            "Commodity_Group"
        ]

        df_small = df[cols + ["quantity"]].copy()

        for c in cols:
            df_small[c] = df_small[c].astype("category")

        df_small["year"] = df_small["year"].astype("int32")

        pivot_df = df_small.pivot_table(
            index=[
                "Continent",
                "ISO3",
                "domain",
                "year",
                "Commodity",
                "Commodity_Group"
            ],
            columns="Scenario",
            values="quantity",
            aggfunc="sum",
            fill_value=0,
            observed=True
        ).reset_index()

        return pivot_df
    
    def pivot_map_forest_data(self):
        df = self.data[dp.forest_db]
        cols = [
            "Continent",
            "ISO3",
            "Scenario",
            "year",
        ]

        df_small = df[cols + ["ForArea","ForStock"]].copy()

        for c in cols:
            df_small[c] = df_small[c].astype("category")

        df_small["year"] = df_small["year"].astype("int32")

        pivot_df_stock = df_small.pivot_table(
            index=[
                "Continent",
                "ISO3",
                "year",
            ],
            columns="Scenario",
            values="ForStock",
            aggfunc="sum",
            fill_value=0,
            observed=True
        ).reset_index()

        pivot_df_area = df_small.pivot_table(
            index=[
                "Continent",
                "ISO3",
                "year",
            ],
            columns="Scenario",
            values="ForArea",
            aggfunc="sum",
            fill_value=0,
            observed=True
        ).reset_index()

        pivot_df_stock["Historic Data"] = 0
        pivot_df_area["Historic Data"] = 0

        return pivot_df_stock, pivot_df_area