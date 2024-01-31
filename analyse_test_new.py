#Import packages
import pandas as pd
import numpy as np
from classes.import_data import package_directory, parameters
from classes.import_data import import_pkl_data
from classes.scenario_plots import sc_plot, PlotDropDown, HeatmapDropDown, InteractivePrice
from classes.model_analysis import validation #not in new
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

#Identify the actual path of this jupyter file
PACKAGEDIR = package_directory()
print(PACKAGEDIR)
print(pd.__version__)#not in old #remove
print(pd.__file__)#not in old #remove
print(np.__version__)#not in old #remove
print(np.__file__)#not in old #remove

#Import data
import_pkl = import_pkl_data()
data = import_pkl.combined_data()
forest_data = data['Forest']
country_data = import_pkl.read_country_data()
forest_data_world = import_pkl.read_forest_data_gfpm(country_data=country_data)
forest_data = forest_data[forest_data_world.columns]
forest_data = pd.concat([forest_data, forest_data_world], axis= 0)
print(forest_data)
forest_data.to_csv('complete_forest_data.csv')
#data = data["data_periods"]#print(data['Forest']) #in new
"""
#Plot predefined scenario results
data = data["data_periods"] #in new 
sc_plot = sc_plot()
sc_plot.predefined_plot(data["data_periods"])

#Validation tables #not in new
validation = validation()
data_vali = validation.model_difference(data=data["data_periods"])
data_quantities = validation.model_corrcoef(data["data_periods"])

#Interactive scenario results (quantities)
plot_dropdown_instance = PlotDropDown(data["data_periods"])

#Interactive scenario results (prices) #not in old
price_interactive = InteractivePrice(data["data_periods"])

#Interactive Heatmap #not in old
data_selection = data['data_periods']

heatmap_dropdown_instance = HeatmapDropDown(data=data_selection)
heatmap_dropdown_instance.update_heatmap_data(reference_data=heatmap_dropdown_instance.reference_data_dropdown.value,
                                              validation_data=heatmap_dropdown_instance.validation_data_dropdown.value,
                                              comparator=heatmap_dropdown_instance.comparator_dropdown.value,
                                              region=heatmap_dropdown_instance.regioncode_dropdown.value,
                                              commodity=heatmap_dropdown_instance.regioncode_dropdown.value,
                                              domain=heatmap_dropdown_instance.domain_dropdown.value
                                              )


"""
#Forestplot

import matplotlib.pyplot as plt
class ForestData:
    def __init__(self, data):
        self.data = forest_data

    def print_forest(self):
        print(self.data)

    def drop_duplicates(self):
        self.data = self.data.drop_duplicates().reset_index(drop=True)
        print('Drop duplicates', self.data)

    def plot_stock_area_diagrams(self):
        scenarios = self.data['Scenario'].unique()
        total_periods = self.data['Period'].unique()

        plt.figure(figsize=(12, 6))
        bar_width = 0.05
        bar_gap = -0.55
        for i, scenario in enumerate(scenarios):
            scenario_name = self.data[self.data['Scenario'] == scenario]
            total_stock = scenario_name.groupby('Period')['ForStock'].sum()

            
            periods_runner = total_stock.index.intersection(total_periods)
            bar_positions = np.arange(len(periods_runner)) + i * (len(periods_runner) * bar_width + bar_gap)
            plt.bar(bar_positions, total_stock[periods_runner], label=f'{scenario} (ForStock)', width=bar_width, align='edge')

        #plt.ylim(ymin=3e6)
        plt.xlabel('Period')
        plt.ylabel('Sum of ForStock')
        plt.legend()
        plt.title('ForStock')
        plt.show()

        plt.figure(figsize=(12, 6))
        for i, scenario in enumerate(scenarios):
            scenario_name = self.data[self.data['Scenario'] == scenario]
            total_area = scenario_name.groupby('Period')['ForArea'].sum()

         
            periods_runner = total_area.index.intersection(total_periods)
            bar_positions = np.arange(len(periods_runner)) + i * (len(periods_runner) * bar_width + bar_gap)
            plt.bar(bar_positions, total_area[periods_runner], label=f'{scenario} (ForArea)', width=bar_width)

        #plt.ylim(ymin=3e7)
        plt.xlabel('Period')
        plt.ylabel('Sum of ForArea')
        plt.legend()
        plt.title('ForArea')
        plt.show()


data_container = data
forest_plot = ForestData(data_container)
forest_plot.drop_duplicates()
forest_plot.print_forest()
forest_plot.plot_stock_area_diagrams()




#Worldmap


