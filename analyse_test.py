#Import packages
import pandas as pd
import numpy as np
from classes.import_data import package_directory, parameters
from classes.import_data import import_pkl_data
from classes.scenario_plots import sc_plot, PlotDropDown
from classes.model_analysis import validation
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

#Identify the actual path of this jupyter file
PACKAGEDIR = package_directory()
print(PACKAGEDIR)

#Import data
import_pkl = import_pkl_data()
data = import_pkl.combined_data()
data = data["data_periods"]

# #Predefined plot
# sc_plot = sc_plot()
# sc_plot.predefined_plot(data)

# #Interactive plot
# plot_dropdown_instance = PlotDropDown(data)

validation = validation()
data_vali = validation.model_difference(data=data)

data_quantities = validation.model_corrcoef(data)