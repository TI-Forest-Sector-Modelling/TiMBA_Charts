![TiMBA Logo](https://raw.githubusercontent.com/TI-Forest-Sector-Modelling/TiMBA_Charts/main/Toolbox/classes/assets/timba_charts_logo.png)

# TiMBA Charts

[![Build Status](https://github.com/TI-Forest-Sector-Modelling/TiMBA_Charts/actions/workflows/actions.yml/badge.svg)](https://github.com/TI-Forest-Sector-Modelling/TiMBA_Charts/actions/workflows/actions.yml)
[![codecov](https://codecov.io/gh/TI-Forest-Sector-Modelling/TiMBA_Charts/graph/badge.svg?token=S4TDJI4CC3)](https://codecov.io/gh/TI-Forest-Sector-Modelling/TiMBA_Charts)
![PyPI](https://img.shields.io/pypi/v/TiMBA_Charts)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![DOI](https://zenodo.org/badge/883749241.svg)](https://zenodo.org/badge/latestdoi/883749241)
[![PyPI Downloads](https://static.pepy.tech/badge/timba-charts)](https://pepy.tech/projects/timba-charts)

This package serves as a toolkit for analysing **TiMBA's** simulation results. TiMBA is a partial economic equilibrium model for the global forest product market. The package provides a dashboard allowing the user to explore TiMBA’s main results. This includes the development of prices, production, consumption, and trade of forest products as well as forest stock development. It further provides information about historic developments as reported by the FAOSTAT. In principle, this toolkit can be easily adapted and used for the analysis of any forest sector model as long as the data resembles the format of the TiMBA output. 

## Cite the package
We are happy that you consider to use TiMBA Charts for your research. When publishing your work in articles, working paper, presentations or elsewhere, please cite the package as:

Morland, C., Tandetzki, J. and Honkomp, T. (2025) TiMBA Charts v.0.2.0

## Install TiMBA Charts

The package is developed and tested with Python 3.12.6 on Windows. Please ensure that Python is installed on your system. It can be downloaded and installed
from [Python.org](https://www.python.org/downloads/release/python-3126/).

### Install via GitHub

1. Clone the repository
Begin by cloning the repository to your local machine using the following command: 
   >git clone https://github.com/TI-Forest-Sector-Modelling/TiMBA_Charts
   > 
2. Switch to the TiMBA Charts directory  
Navigate into the project folder on your local machine.
   >cd TiMBA_Charts
   >
3. Create a virtual environment  
It is recommended to set up a virtual environment for TiMBA Charts to manage dependencies. If you are using only a single version of Python on your computer:
   >python -m venv .venv
   >
1. Activate the virtual environment  
Enable the virtual environment to isolate TiMBA Charts dependencies. 
   >.venv\Scripts\activate
   >
1. Install TiMBA Charts in the editable mode  
   >pip install -e .

If the following error occurs: "ERROR: File "setup.py" or "setup.cfg" not found."
you might need to update the pip version you use with: 
>python.exe -m pip install --upgrade pip

### Install via Pypi
   >pip install timba-charts

Note: The module requires input data from TiMBA simulations. Before proceeding, please ensure that the simulation results are stored in .../Toolbox/Input/Scenario_Files/ or in the file path specified with the CLI command show_dashboard -FP=. Otherwise, the dashboards will not open.

The same applies to the additional information, which must be located in .../Toolbox/Input/Additional_Information/ or in the path provided with show_dashboard -AIFP=.

## Start the default dashbord
After installing the package, the user can start the dashboard board with the following CLI command:
> show_dashboard

Following CLI command can be used to show all changeable options with the CLI:
> show_dashboard --help

At the moment, two options can be changed. The specification of the number of most recent .pkl files to read and 
the definition of the folder path where the scenario results are stored.

The number of scenarios can be changed as follows:
> show_dashboard -NF=4

To change the folder path the user can type, e.g.:
> show_dashboard -FP='E:\P_TiMBA\TiMBA\data\output'

### Description of the figures
The interactive dashboard provides a flexible interface for exploring model outputs across multiple dimensions. Users can apply filters by region (country or continent), scenario, domain (e.g. Demand, Supply, Trade, Net Trade, and Manufacturing), commodity (ranging from 16 to 20, depending on the input scenario), and commodity group via a control panel. 

Please note that certain filter combinations are interdependent and may not return any results. For instance, selecting Roundwood under demand domain will yield no output, as roundwood is a primary good for which only supply is modeled. Likewise, applying both the commodity and commodity group filters simultaneously will not narrow the selection further, as these categories are not hierarchically structured.

Based on the selected inputs, four visualizations are updated dynamically to support intuitive analysis and comparison of model results:  

1. The central time series plot displays the development of selected quantities over time. Historical data are represented by solid lines, while scenario-based projections appear as dashed lines. This visualization facilitates an understanding of long-term trends and the dynamics of different scenarios across commodities or commodity groups.  

2. The bar chart in the bottom left presents world market prices by year and scenario. It offers a concise overview of price developments across time periods and enables straightforward temporal comparisons.  

3. The top-right chart depicts changes in forest stock over time and across scenarios. Each bar represents a specific year or period, illustrating how stock levels evolve under different assumptions.  

4. The world map in the bottom right provides a spatial representation of the selected indicator for a given year. Countries are color-coded using a gradient scale (with deeper green indicating higher values). Users can explore different domain–product combinations, such as the product Roundwood and the domain Supply, which reveal which countries exhibit the highest levels of roundwood production. This logic applies to any domain–product selection. A specific year can also be chosen within the map filter to examine spatial patterns in more detail. Please note that this map will always show an aggregate over all scenarios. If the user wanted to show only historical data or a specific scenario this can be chosen by the scenario filter.
   
For any combination of filters users will have the option to export the filtered dataset as a csv file or the different graphs as png files for further analysis or documentation.  

## Start the validation dashbord
After installing the package, the user can start the dashboard board with the following CLI command:
> show_validation

### Description of the figures

## Authors
- [Christian Morland](https://www.thuenen.de/de/fachinstitute/waldwirtschaft/personal/wissenschaftliches-personal/ehemalige-liste/christian-morland-msc) [(ORCID 0000-0001-6600-570X)](https://orcid.org/0000-0001-6600-570X),
- [Julia Tandetzki](https://www.thuenen.de/de/fachinstitute/waldwirtschaft/personal/wissenschaftliches-personal/julia-tandetzki-msc) [(ORCID 0000-0002-0630-9434)](https://orcid.org/0000-0002-0630-9434) and 
- [Tomke Honkomp](https://www.thuenen.de/de/fachinstitute/waldwirtschaft/personal/wissenschaftliches-personal/tomke-honkomp-msc) [(ORCID 0000-0002-6719-0190)](https://orcid.org/0000-0002-6719-0190). 

## License and copyright note
Copyright ©, 2025, Thuenen Institute, Christian Morland, Julia Tandetzki, 
Tomke Honkomp, wf-timba@thuenen.de

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program.  If not, see
<https://www.gnu.org/licenses/>.


