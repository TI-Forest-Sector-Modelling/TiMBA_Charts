import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import os
from enum import Enum

def package_directory():
    PACKAGEDIR = Path(__file__).parent.parent.absolute()
    return PACKAGEDIR
PACKAGEDIR = package_directory()

class parameters(Enum):
    input_folder = "\\Input"
    seperator_scenario_name = "Sc_"
    column_name_scenario = "Scenario"
    column_name_model = "Model"
    column_name_id = "ID"
    model_name = "GFPMpt"
    csv_input = "GFPM_results_World500.csv"
    #csv_input_forest = ''

class import_pkl_data():
    def init(self):
        pass

    def open_pickle(self, src_filepath: str):
        """open pkl file
        :param src_filepath: source path for pkl file
        :return: object from pkl file
        """
        import pickle
        with open(src_filepath, "rb") as pkl_file:
            obj = pickle.load(pkl_file)
        return obj

    def read_pkl(self, data):
        """read data container from pkl file and store it within dictionary
        :return: dictionary of data container
        """
        data_container = {"Forest": data["Forest"], 
                        "ManufactureCost": data["ManufactureCost"], 
                        "results_agg": data["data_aggregated"],
                        "results": data["data_periods"],
                        "WorldPrices": data["WorldPrices"]}
        return data_container
    
    def downcasting(self, data: pd.DataFrame):
        data.RegionCode = data.RegionCode.astype("category")
        data.CommodityCode = data.CommodityCode.astype("category")
        data.domain = data.domain.astype("category")
        data.price = data.price.astype("float32")
        data.quantity = data.quantity.astype("float32")
        data.elasticity_price = data.elasticity_price.astype("float32")
        data.slope = data.slope.astype("float32")
        data.intercept = data.intercept.astype("float32")
        data.Period = data.Period.astype("int16")
        data.year = data.year.astype("int16")
        data.shadow_price = data.shadow_price.astype("float32")
        data.lower_bound = data.lower_bound.astype("float32")
        data.upper_bound = data.upper_bound.astype("float32")
        data.Scenario = data.Scenario.astype("category")
        data.Model = data.Model.astype("category")
        data.ID = data.ID.astype("category")
        return data

    def concat_scenarios(self, data, sc_name:str, data_prev, ID):
        """concat_scenarios, add scenario name from pkl file to data frames
        :param data: dictionary of the data container
        :param sc_name: scenario name from file name in dictionary
        """    
        for key in data: #loop through all data from datacontainer
            data[key][parameters.column_name_scenario.value] = sc_name
            data[key][parameters.column_name_model.value] = parameters.model_name.value
            data[key][parameters.column_name_id.value] = ID
            if data_prev != []:
                data[key] = pd.concat([data_prev[key], data[key]], axis=0)
                
    def combined_data(self):
        """loop trough all input files in input directory
        """
        file_list = os.listdir(str(PACKAGEDIR) + parameters.input_folder.value)
        data_prev = []
        ID = 1
        for scenario_files in file_list:
            src_filepath = str(PACKAGEDIR) + parameters.input_folder.value + "\\" + scenario_files
            scenario_name = scenario_files[scenario_files.rfind(parameters.seperator_scenario_name.value)+3
                                        :-4]
            try:
                data = self.open_pickle(src_filepath)
                print(data)
                #data = self.read_pkl(data=data_container)
                self.concat_scenarios(data=data, sc_name=scenario_name, data_prev=data_prev, ID=ID)
            except pickle.UnpicklingError:
                pass
            data_prev = data
            ID += 1
        
        data_prev["data_periods"] = self.downcasting(data_prev["data_periods"])
        data = pd.read_csv(str(PACKAGEDIR) + parameters.input_folder.value + "\\" + parameters.csv_input.value)
        data = self.downcasting(data)
        data = pd.read_csv(str(PACKAGEDIR) + parameters.input_folder.value + "\\" + parameters.csv_input.value)
        data_results = pd.concat([data_prev["data_periods"], data], axis=0)
        data_prev["data_periods"] = data_results

        return data_prev
    
    def julias_data():
        file_path = "data.xlsx"
        data = pd.read_excel(file_path)
        data.head()
        return data