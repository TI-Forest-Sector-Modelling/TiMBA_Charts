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
        """combine all data imports
        """
        forest_data = self.data[dp.forest_db]
        self.data[dp.forest_formip_db] = self.data[dp.forest_db] 
        forest_data = forest_data[['Scenario','RegionCode','Period','ForStock','ForArea','supply_from_forest']]
        forest_data = forest_data.drop_duplicates(subset=['Scenario', 'RegionCode', 'Period'], keep='first')
        self.data[dp.overview_db] = pd.merge(self.data[dp.overview_db], forest_data, how='left', on=['Scenario','RegionCode','Period'])
        year_df= self.data[dp.overview_db][["Period","year"]].drop_duplicates()
        year_dict = dict(zip(year_df["Period"],year_df["year"]))
        self.data[dp.overview_db] = pd.concat([self.data[dp.overview_db], self.data_hist], axis=0)
        self.data[dp.overview_db] = pd.merge(self.data[dp.overview_db], self.country_data, on="RegionCode", how="left")
        self.data[dp.overview_db] = pd.merge(self.data[dp.overview_db], self.commodity_data, on="CommodityCode", how="left")
        self.data[dp.overview_db]["domain"] = self.data[dp.overview_db]["domain"].replace({
            'ManufactureCost': 'Manufacturing',
            'TransportationExport': 'Export',
            'TransportationImport': 'Import',
            })
        self.data[dp.overview_db] = self.data[dp.overview_db][['Model','Scenario','RegionCode','Continent','Country','ISO3',
                                                               'CommodityCode','Commodity','Commodity_Group','Period','year',
                                                               'domain','price','quantity',
                                                               'ForStock','ForArea',
                                                               ]]
        country_dict = dict(zip(self.country_data["RegionCode"], self.country_data["ISO3"]))
        continent_dict = dict(zip(self.country_data["RegionCode"], self.country_data["Continent"]))
        forest_data["ISO3"] = forest_data["RegionCode"].map(country_dict)
        forest_data["Continent"] = forest_data["RegionCode"].map(continent_dict)
        forest_data["year"] = forest_data["Period"].map(year_dict)
        print(forest_data)
        self.data[dp.forest_db] = forest_data
        return self.data