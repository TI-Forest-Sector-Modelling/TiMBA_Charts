from pathlib import Path

PACKAGEDIR = Path(__file__).resolve().parent.parent.parent
SCINPUTPATH = Path("Scenario_Files")
AIINPUTPATH = Path("Additional_Information")
SCFOLDERPATH = Path("Toolbox") / Path("Input")

# Input to adress data storage in GIT Repo
GIT_USER = "TI-Forest-Sector-Modelling"
GIT_REPO = "TiMBA_Additional_Information"
GIT_BRANCH = "4-add-output-for-default_scenario"
SCINPUT_GITHUB_URL = "Output_Data/default_scenario"
AIINPUT_GITHUB_URL = "Input_Data/default_scenario/02_Additional_Information"

COUNTRYINFO = "country_info.csv"
COMMODITYINFO = "commodity_info.csv"
FORESTINFO = "Forest_world500.csv"
HISTINFO = "FAO_Data.csv"
FORMIP = "external_model_data.csv"
addinfo_file_list = [COUNTRYINFO, COMMODITYINFO, FORESTINFO, HISTINFO, FORMIP]
