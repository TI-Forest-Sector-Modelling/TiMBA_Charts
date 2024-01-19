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
#data = data["data_periods"]#print(data['Forest']) #in new

#Plot predefined scenario results
#data = data["data_periods"] #in new 
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

#Forest Plots #not in old
def forest_data_read_world500(file_name): #shift to import data
    file_path = f'input/{file_name}'
    try: 
        data = pd.read_csv(file_path)
        return data
    except FileNotFoundError: 
        print('Forest data not applicable')
        return None

if __name__ == '__main__':
    forest_data_world500 = 'Forest_Area_world500.csv'
    forest_data_world500 = forest_data_read_world500(forest_data_world500)

    if forest_data_world500 is not None:
        print(forest_data_world500) #shift to import data

#
import pandas as pd #shift to sc plot
import matplotlib.pyplot as plt
import numpy as np

class ForestData:
    def __init__(self, data):
        self.data = data['Forest']

    def print_forest(self):
        print(self.data)
    
    def drop_duplicates(self):
        self.data = self.data.drop_duplicates().reset_index(drop=True)

    def plot_stock_area_diagrams(self):
        unique_scenarios = self.data['Scenario'].unique()
        all_periods = self.data['Period']

        plt.figure(figsize=(12, 6))
        bar_width = 0.15
        bar_gap = 0.3
        for i, period in enumerate(all_periods):
            for j, scenario in enumerate(unique_scenarios):
                scenario_data = self.data[(self.data['Scenario'] == scenario) & (self.data['Period'] == period)]
                total_stock = scenario_data['ForStock']

                
                plt.bar(i * len(unique_scenarios) + j * (bar_width + bar_gap), total_stock.iloc[0], label=f'{scenario} (Period {period})', width=bar_width)

        plt.xlabel('Scenarios')
        plt.ylabel('ForStock')
        plt.xticks(np.arange(len(all_periods) * len(unique_scenarios)) * (bar_width + bar_gap) + bar_width/2, [f'Period {p}' for p in all_periods])
        plt.legend()
        plt.title('ForStock for Each Scenario in All Periods')
        plt.show()

        plt.figure(figsize=(10, 6))
        for i, scenario in enumerate(unique_scenarios):
            scenario_data = self.data[self.data['Scenario'] == scenario]
            total_area = scenario_data.groupby('Period')['ForArea'].sum()

            
            existing_periods = total_area.index.intersection(all_periods)
            plt.bar(existing_periods + i * (bar_width + bar_gap), total_area[existing_periods], label=scenario, width=bar_width)


        plt.xlabel('Period')
        plt.ylabel('Sum of ForArea')
        plt.legend()
        plt.title('ForArea')
        plt.show()

if __name__ == "__main__": #shift to sc plot
    data_container = data
    forest_instance = ForestData(data_container)
    forest_instance.print_forest()
    forest_instance.plot_stock_area_diagrams()






#Worldmap


