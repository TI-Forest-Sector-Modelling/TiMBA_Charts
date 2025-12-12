from pathlib import Path

PACKAGEDIR = Path(__file__).resolve().parent.parent
SCINPUTPATH = PACKAGEDIR / Path("Input") / Path("Scenario_Files")
AIINPUTPATH = PACKAGEDIR / Path("Input") / Path("Additional_Information")
SCFOLDERPATH = Path("Input")

TIMBA_DATA_REPO_URL = "https://github.com/TI-Forest-Sector-Modelling/TiMBA_Additional_Information/archive/refs/heads/4-add-output-for-default_scenario.zip"
SCINPUT_GITHUB_URL = "TiMBA_Additional_Information-4-add-output-for-default_scenario/Output_Data/default_scenario"
AIINPUT_GITHUB_URL = "TiMBA_Additional_Information-4-add-output-for-default_scenario/Input_Data/default_scenario/02_Additional_Information"

COUNTRYINFO = "country_info.csv"
COMMODITYINFO = "commodity_info.csv"
FORESTINFO = "Forest_world500.csv"
HISTINFO = "FAO_Data.csv"
FORMIP = "external_model_data.csv"
addinfo_file_list = [COUNTRYINFO, COMMODITYINFO, FORESTINFO, HISTINFO, FORMIP]

SCFILE = "DataContainer_Sc_scenario_input.pkl"
scenario_file_list = [SCFILE]

