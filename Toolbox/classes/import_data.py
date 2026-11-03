import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import os
from enum import Enum
import pickle
import gzip
import Toolbox.parameters.paths as toolbox_paths
import Toolbox.parameters.default_parameters as toolbox_parameters

class import_pkl_data:
    def __init__(self, num_files_to_read:int=25,
                 SCENARIOPATH:Path= toolbox_paths.SCINPUTPATH,
                 ADDINFOPATH:Path= toolbox_paths.AIINPUTPATH):
        self.num_files_to_read = num_files_to_read
        self.SCENARIOPATH = SCENARIOPATH
        self.ADDINFOPATH = ADDINFOPATH

    def open_pickle(self, src_filepath: str):
        """open pkl file
        :param src_filepath: source path for pkl file
        :return: object from pkl file
        """
        import pickle
        with open(src_filepath, "rb") as pkl_file:
            obj = pickle.load(pkl_file)
        return obj

    def read_country_data(self):
        """read data additional information for country data
        :return: country data
        """
        country_data = pd.read_csv(self.ADDINFOPATH / toolbox_paths.COUNTRYINFO, encoding = "ISO-8859-1")
        country_data = country_data[["Country-Code", "ContinentNew", "Country","ISO-Code"]]
        country_data.columns = ["RegionCode","Continent", "Country","ISO3"]
        country_data.Country = country_data.Country.astype("category")
        country_data.Continent = country_data.Continent.astype("category")
        country_data.ISO3 = country_data.ISO3.astype("category")
        return country_data
    
    def read_commodity_data(self):
        """read data additional information for commodity data
        :return: commodity data
        """
        commodity_data = pd.read_csv(self.ADDINFOPATH / toolbox_paths.COMMODITYINFO , encoding = "ISO-8859-1")
        commodity_data = commodity_data[["Commodity","CommodityCode","Commodity_Group"]]
        commodity_data.Commodity = commodity_data.Commodity.astype("category")
        commodity_data.CommodityCode = commodity_data.CommodityCode.astype("category")
        commodity_data.Commodity_Group = commodity_data.Commodity_Group.astype("category")
        return commodity_data
    
    def read_historic_data(self):
        data = pd.read_csv(self.ADDINFOPATH / toolbox_paths.HISTINFO)
        data = self.downcasting(data)
        return data
        
    def downcasting(self, data: pd.DataFrame):
        data.RegionCode = data.RegionCode.astype("category")
        data.CommodityCode = data.CommodityCode.astype("category")
        data.domain = data.domain.astype("category")
        data.price = data.price.astype("float32")
        data.quantity = data.quantity.astype("float32")
        data.Period = data.Period.astype("int16")
        data.year = data.year.astype("int16")
        data.Scenario = data.Scenario.astype("category")
        data.Model = data.Model.astype("category")
        return data
    
    def add_consumption(self, data):
        data["quantity"] = (data["quantity_ManufactureCost"] +
                            data["quantity_Supply"] -
                            data["quantity_TransportationExport"] +
                            data["quantity_TransportationImport"])
        data.loc[data["quantity"] < 0, "quantity"] = 0
        data["price"] = (((data["quantity_ManufactureCost"] * data["price_ManufactureCost"]) +
                          (data["quantity_Supply"] * data["price_Supply"]) -
                          (data["quantity_TransportationExport"] * data["price_TransportationExport"]) +
                          (data["quantity_TransportationImport"]* data["price_TransportationImport"]))/
                          data["quantity"])
        data["price"] = 0
        data["domain"] = "Consumption"
        return data
    
    def add_net_exports(self, data):
        data["quantity"] =  (data["quantity_TransportationExport"] -
                            data["quantity_TransportationImport"])
        data["price"] =  data["price_TransportationExport"]
        data["domain"] = "Net Exports"
        return data
    
    def add_net_imports(self, data):
        data["quantity"] =  (data["quantity_TransportationImport"] -
                            data["quantity_TransportationExport"])
        data["price"] = data["price_TransportationImport"]
        data["domain"] = "Net Imports"
        return data
    
    def add_production(self, data):
        data["quantity"] =  (data["quantity_ManufactureCost"] + data["quantity_Supply"])
        data["price"] = (((data["quantity_ManufactureCost"] * data["price_ManufactureCost"]) +
                          (data["quantity_Supply"] * data["price_Supply"])) / data["quantity"])
        # if data["price"].mean() <=0:
        #     data["price"] = 0
        data["domain"] = "Production"
        return data
    
    def concat_calc_domains(self,origin_data:pd.DataFrame,calc_data:pd.DataFrame):
        calc_data = calc_data[['RegionCode','CommodityCode','Period','year','domain','price','quantity']].reset_index(drop=True) 
        result_df = pd.concat([origin_data, calc_data], axis=0).reset_index(drop=True) 
        return result_df

    def add_calculated_domains(self,data:pd.DataFrame):
        pivoted_price = data["data_periods"].pivot(index=["RegionCode", "CommodityCode", "Period", "year"], 
                         columns="domain", 
                         values="price").add_prefix("price_")
        pivoted_quantity = data["data_periods"].pivot(index=["RegionCode", "CommodityCode", "Period", "year"], 
                                    columns="domain", 
                                    values="quantity").add_prefix("quantity_")
        pivoted_df = pd.concat([pivoted_price, pivoted_quantity], axis=1).reset_index()    

        calculated_functions = [#"add_consumption",
                                "add_net_exports",
                                "add_net_imports",
                                #"add_production",
                                ]
        for method_name in calculated_functions:
            calc_df = getattr(self, method_name)(data=pivoted_df)
            data["data_periods"] = self.concat_calc_domains(origin_data=data["data_periods"], calc_data=calc_df)

        return data["data_periods"]

    def concat_scenarios(self, data: pd.DataFrame, sc_name:str, data_prev: pd.DataFrame, ID: int):
        """concat_scenarios, add scenario name from pkl file to data frames
        :param data: dictionary of the data container
        :param sc_name: scenario name from file name in dictionary
        """    
        data["data_periods"] = self.add_calculated_domains(data=data)
        try:
            for key in data: #loop through all data from datacontainer
                data[key][toolbox_parameters.column_name_scenario] = sc_name
                data[key][toolbox_parameters.column_name_model] = toolbox_parameters.model_name
                #data[key][parameters.column_name_id.value] = ID
                if data_prev != []:
                    data[key] = pd.concat([data_prev[key], data[key]], axis=0)
        except KeyError:
            pass
                
    def combined_data(self):
        """loop trough all input files in input directory
        """
        scenario_path = self.SCENARIOPATH
        num_files_to_read = self.num_files_to_read
        pkl_files = [
            Path(scenario_path) / file
            for file in os.listdir(scenario_path)
            if file.endswith(".pkl")
        ]
        sorted_files = sorted(pkl_files, key=lambda x: x.stat().st_mtime, reverse=True)
        newest_files = sorted_files[:num_files_to_read]

        data = []
        data_prev = []
        ID = 1
        for scenario_files in newest_files:
            src_filepath = scenario_path / scenario_files
            print(src_filepath)
            scenario_name = str(scenario_files)[str(scenario_files).rfind(toolbox_parameters.seperator_scenario_name)+3
                                        :-4]
            try:
                with gzip.open(src_filepath,'rb') as f:
                    if type(f) == gzip.GzipFile:
                        data = pickle.load(f)
                        data['data_periods'] = data['data_periods'][['RegionCode','CommodityCode','Period','year','domain','price','quantity']]
                self.concat_scenarios(data=data, sc_name=scenario_name, data_prev=data_prev, ID=ID)
            except gzip.BadGzipFile:
                pass
            except pickle.UnpicklingError:
                pass
            except PermissionError:
                pass
            except ValueError:
                pass

            data_prev = data
            ID += 1
        
        data_prev["data_periods"] = self.downcasting(data_prev["data_periods"])
        try:
            data = self.read_historic_data()
        except FileNotFoundError:
            data = pd.DataFrame()
        country_data = self.read_country_data()
        commodity_data = self.read_commodity_data()
        forest_data = data_prev['Forest']
        forest_data = forest_data[['Scenario','RegionCode','Period','ForStock','ForArea']]
        forest_data = forest_data.drop_duplicates(subset=['Scenario', 'RegionCode', 'Period'], keep='first')
        data_prev["data_periods"] = pd.merge(data_prev["data_periods"], forest_data, how='left', on=['Scenario','RegionCode','Period'])
        data_prev["data_periods"] = pd.concat([data_prev["data_periods"], data], axis=0)
        data_prev["data_periods"] = pd.merge(data_prev["data_periods"], country_data, on="RegionCode", how="left")
        data_prev["data_periods"] = pd.merge(data_prev["data_periods"], commodity_data, on="CommodityCode", how="left")
        data_prev["data_periods"]["domain"] = data_prev["data_periods"]["domain"].replace({
            'ManufactureCost': 'Manufacturing',
            'TransportationExport': 'Export',
            'TransportationImport': 'Import',
            })
        data_prev["data_periods"] = data_prev["data_periods"][['Model','Scenario','RegionCode','Continent','Country','ISO3',
                                                               'CommodityCode','Commodity','Commodity_Group','Period','year',
                                                               'domain','price','quantity',
                                                               'ForStock','ForArea',
                                                               ]]
        return data_prev

    def read_forest_data_gfpm(self, country_data:pd.DataFrame):
        for_data_gfpm = pd.read_csv(self.ADDINFOPATH / toolbox_paths.FORESTINFO, encoding = "ISO-8859-1")
        
        rearranged_for_data = pd.melt(for_data_gfpm, id_vars=['domain','Country'], var_name='Year',value_name='for')
        rearranged_for_data = rearranged_for_data.dropna()
        rearranged_for_data['Year'] = rearranged_for_data['Year'].astype(int)

        foreststock = pd.DataFrame()        
        for domain in rearranged_for_data.domain.unique():
            rearranged_for_data_domain = rearranged_for_data[rearranged_for_data['domain'] == domain].reset_index(drop=True)
            if domain == 'ForArea':
                rearranged_for_data_domain['ForStock'] = foreststock
            else: 
                foreststock = rearranged_for_data_domain['for']
        forest_data = rearranged_for_data_domain[['Country', 'Year', 'for', 'ForStock']]
        forest_data.columns = ['Country', 'Year', 'ForArea', 'ForStock']
        forest_data = pd.merge(forest_data, country_data, on= 'Country')

        period_mapping = {2017: 0, 2020: 1, 2025: 2, 2030: 3, 2035: 4, 2040: 5, 2045: 6, 2050: 7, 2055: 8, 2060: 9, 2065: 10}
        forest_data['Period'] = forest_data['Year'].map(period_mapping)

        forest_gfpm = forest_data[['RegionCode', 'Period', 'ForStock', 'ForArea']]
        forest_gfpm[toolbox_parameters.column_name_scenario]= 'world500'
        forest_data['Model'] = 'GFPM'
        return forest_gfpm
    
if __name__ == "__main__":
    import_pkl = import_pkl_data()
    data = import_pkl.combined_data()
    print(data['data_periods'])