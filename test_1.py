import pandas as pd
import numpy as np
from classes.import_data import package_directory, parameters
from classes.import_data import import_pkl_data
from classes.scenario_plots import sc_plot, PlotDropDown
#from classes.model_analysis import validation
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from enum import Enum
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import os
import matplotlib.pyplot as plt

#Identify the actual path of this jupyter file
PACKAGEDIR = package_directory()
print(PACKAGEDIR)



class parameters(Enum):
    input_folder = "\\Input"
    seperator_scenario_name = "Sc_"
    column_name_scenario = "Scenario"
    column_name_model = "Model"
    column_name_id = "ID"
    model_name = "GFPMpt"
    csv_input = "GFPM_results_World500.csv"
    csv_input_forest = 'Forest_Area_world500.csv'

# class import_pkl_data():
#     def init(self):
#         pass

#     def open_pickle(self, src_filepath: str):
#         """open pkl file
#         :param src_filepath: source path for pkl file
#         :return: object from pkl file
#         """
#         import pickle
#         with open(src_filepath, "rb") as pkl_file:
#             obj = pickle.load(pkl_file)
#         return obj

#     def read_pkl(self, data):
#         """read data container from pkl file and store it within dictionary
#         :return: dictionary of data container
#         """
#         data_container = {"Forest": data["Forest"], 
#                         "ManufactureCost": data["ManufactureCost"], 
#                         "results_agg": data["data_aggregated"],
#                         "results": data["data_periods"],
#                         "WorldPrices": data["WorldPrices"]}
#         return data_container
    
#     def downcasting(self, data: pd.DataFrame):
#         data.RegionCode = data["Forest"].RegionCode.astype("category")
#         data.ForStock = data.ForStock.astype("float32")
#         data.ForArea = data.ForArea.astype("float32")
#         data.Period = data.Period.astype("int16")
#         data.Scenario = data.Scenario.astype("category")
#         data.Model = data.Model.astype("category")
#         data.ID = data.ID.astype("category")
#         return data

#     def concat_scenarios(self, data, sc_name:str, data_prev, ID):
#         """concat_scenarios, add scenario name from pkl file to data frames
#         :param data: dictionary of the data container
#         :param sc_name: scenario name from file name in dictionary
#         """    
#         for key in data: #loop through all data from datacontainer
#             if key == 'data_aggregated':
#                 pass
#             else:
#                 data[key][parameters.column_name_scenario.value] = sc_name
#                 data[key][parameters.column_name_model.value] = parameters.model_name.value
#                 data[key][parameters.column_name_id.value] = ID
#                 if data_prev != []:
#                     data[key] = pd.concat([data_prev[key], data[key]], axis=0)
                
#     def combined_data(self):
#         """loop trough all input files in input directory
#         """
#         file_list = os.listdir(str(PACKAGEDIR) + parameters.input_folder.value)
#         data_prev = []
#         ID = 1
#         for scenario_files in file_list:
#             src_filepath = str(PACKAGEDIR) + parameters.input_folder.value + "\\" + scenario_files
#             scenario_name = scenario_files[scenario_files.rfind(parameters.seperator_scenario_name.value)+3
#                                         :-4]
#             try:
#                 data = self.open_pickle(src_filepath)
#                 print(data)
#                 #data = self.read_pkl(data=data_container)
#                 self.concat_scenarios(data=data, sc_name=scenario_name, data_prev=data_prev, ID=ID)
#             except pickle.UnpicklingError:
#                 pass
#             data_prev = data
#             ID += 1
    
#         data_prev["Forest"] = self.downcasting(data_prev["Forest"])
#         data = pd.read_csv(str(PACKAGEDIR) + parameters.input_folder.value + "\\" + parameters.csv_input.value)
#         data = self.downcasting(data)
#         data = pd.read_csv(str(PACKAGEDIR) + parameters.input_folder.value + "\\" + parameters.csv_input.value)
#         data_results = pd.concat([data_prev["Forest"], data], axis=0)
#         data_prev["Forest"] = data_results


#     #Import data
# import_pkl = import_pkl_data()
# #data= pd.data['Forest']
# data = import_pkl.combined_data()
# print(data['Forest'])

# data['Forest'] = data['Forest'].drop_duplicates().reset_index(drop=True)

# #print(data)
# #print(data['Forest'])


import_pkl = import_pkl_data()
data = import_pkl.combined_data()
print(data['Forest'])

class Plot_forest:
    def __init__(self, data):
        self.data = data
        self.drop_duplicates()
  
    def drop_duplicates(self):
        self.data['Forest'] = self.data['Forest'].drop_duplicates().reset_index(drop=True)
        return self.data
    
    def plot_sum(self):
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))

        sum_stock = {}
        sum_area = {}
        width = 0.2
        #value = self.data['Forest']
        #value.ForStock = value.ForStock.astype("float32")
        #value.ForArea = value.ForArea.astype("float32")
        #value.Scenario = value.Scenario.astype("category")
        for key, value in self.data['Forest']():
            sum_stock[key] = value.groupby('Period')['ForStock'].sum()
            sum_area[key] = value.groupby('Period')['ForArea'].sum()


        for i, (key, value) in enumerate(sum_stock.items()):
            axs[0].bar(np.arange(len(value)) + i * width, value.values, width=width, label=key)

        sum_area = value.groupby(['Scenario', 'Period'])['ForArea'].sum().reset_index()
        print(sum_stock)
        print(sum_area)
        
        axs[0].bar(sum_stock.Period, sum_stock.ForStock)

        axs[0].set_xlabel('Period')
        axs[0].set_ylabel('Sum of ForStock')
        axs[0].legend(loc='upper right')

        axs[1].bar(sum_area.Period, sum_area.ForArea)

        axs[1].set_xlabel('Period')
        axs[1].set_ylabel('Sum of ForArea')
        axs[1].legend(loc='lower center')

        plt.show()

if __name__ == "__main__":   
    plot = Plot_forest(data)
    plot.plot_sum()