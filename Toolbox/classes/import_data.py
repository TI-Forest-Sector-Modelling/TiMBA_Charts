import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import os
from enum import Enum
import pickle
import gzip
import requests
from io import BytesIO
import zipfile
from urllib.error import URLError
import os
import shutil
import tempfile
import zipfile
import urllib.request
import Toolbox.parameters.paths as toolbox_paths
import Toolbox.parameters.default_parameters as toolbox_parameters
from Toolbox.parameters.defines_geo import CountryGroups


class import_pkl_data:
    def __init__(self,
                 num_files_to_read: int,
                 SCENARIOPATH: Path,
                 ADDINFOPATH: Path):
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


class import_formip_data:
    def __init__(self,
                 ADDINFOPATH:Path= toolbox_paths.AIINPUTPATH,
                 timba_data:pd.DataFrame=pd.DataFrame(),
                 only_baseline_sc:bool=True):
        self.FORMIPPATH = ADDINFOPATH / toolbox_paths.FORMIP
        self.formip_data = self.read_formip_data()
        self.timba_data = timba_data
        self.only_baseline_sc = only_baseline_sc
        self.ADDINFOPATH = ADDINFOPATH

    def read_formip_data(self):
        """
        Reads in data from the Forest sector model intercomparison (ForMIP) project (Daigneault et al. 2022)
        :return: ForMIP data
        """
        formip_data = pd.read_csv(self.FORMIPPATH)
        return formip_data

    def process_formip_data(self):
        """
        Processes ForMIP data for further visualization. Data for missing years are linearly interpolated.
        :return: Processed FORMIP data
        """
        formip_data = self.formip_data
        formip_data_info = formip_data.iloc[:, :6].copy()
        formip_data = formip_data.iloc[:, 6:].copy()
        year_list = formip_data.columns.tolist()

        year_runner = 0
        for year_next in year_list[1:]:
            year_prev = year_list[year_runner]

            data_next = formip_data[year_next]
            data_prev = formip_data[year_prev]
            data_diff = (data_next - data_prev) / (int(year_next) - int(year_prev))

            year_to_fill = range(int(year_prev) + 1, int(year_next))

            for year in year_to_fill:
                formip_data[str(year)] = formip_data[str(year - 1)] + data_diff

            year_runner += 1

        formip_data_new = pd.DataFrame()
        for year in formip_data.columns:
            formip_data_tmp = formip_data[year]
            formip_data_info_tmp = formip_data_info.copy()
            formip_data_info_tmp["Year"] = int(year)
            formip_data_info_tmp["Data"] = formip_data_tmp
            formip_data_new = pd.concat([formip_data_new, formip_data_info_tmp], axis=0).reset_index(drop=True)

        formip_data_new = formip_data_new.sort_values(by=["Model", "RCP-SSP", "Region", "Year"],
                                                      ascending=True).reset_index(drop=True)
        if self.only_baseline_sc:
            scenario_filter = ["Baseline-SSP1", "Baseline-SSP2", "Baseline-SSP3", "Baseline-SSP4", "Baseline-SSP5"]
            formip_data_new = formip_data_new[formip_data_new["RCP-SSP"].isin(scenario_filter)].reset_index(drop=True)

        if "Carbon" not in self.timba_data.keys():
            formip_data_new = formip_data_new[
                formip_data_new["Estimate"] != "Total Forest Non-soil C Stock (MtC)"].reset_index(drop=True)

        formip_data_new = formip_data_new[(formip_data_new["Estimate"] != "Carbon Price (/tCO2e)") &
                                          (formip_data_new["Estimate"] != "Wt Avg Roundwood Price (/m3)")].reset_index(drop=True)

        return formip_data_new

    def process_timba_data(self):
        """
        Processes TiMBA scenario results to match ForMIP data structure.
        :return:
        """

        geo_data = pd.read_csv(self.ADDINFOPATH / toolbox_paths.COUNTRYINFO,
                               encoding = "ISO-8859-1")
        geo_data = geo_data[["Country-Code", "ISO-Code"]]

        timba_data_prod = self.timba_data["data_periods"].copy().reset_index(drop=True)
        timba_data_forest = self.timba_data["Forest"].copy().reset_index(drop=True)
        try:
            timba_data_carbon = self.timba_data["Carbon"].copy().reset_index(drop=True)
        except KeyError:
            pass

        timba_data_prod = timba_data_prod[(timba_data_prod["domain"] == "Supply") &
                                          (timba_data_prod["Model"] == "TiMBA")].reset_index(drop=True)

        period_structure = timba_data_prod[["Period", "year"]].drop_duplicates().reset_index(drop=True)
        timba_data_forest = timba_data_forest.merge(geo_data, left_on="RegionCode", right_on="Country-Code",
                                                    how="left")
        timba_data_forest = timba_data_forest[
            ["Model", "RegionCode", "ISO-Code", "Scenario", "Period", "ForStock", "ForArea"]].drop_duplicates()
        timba_data_forest = timba_data_forest.merge(
            period_structure, left_on=["Period"], right_on=["Period"], how="left")

        try:
            timba_data_carbon = timba_data_carbon.merge(
                period_structure, left_on=["Period"], right_on=["Period"], how="left")
        except UnboundLocalError:
            pass

        for region in CountryGroups.formip_regions.value.keys():
            region_iso = CountryGroups.formip_regions.value[region]

            region_iso_index_forest = pd.DataFrame([x in region_iso for x in timba_data_forest["ISO-Code"]])
            region_iso_index_forest = region_iso_index_forest[region_iso_index_forest[0] == True].index
            timba_data_forest.loc[region_iso_index_forest, "Region"] = region

            region_iso_index_prod = pd.DataFrame([x in region_iso for x in timba_data_prod["ISO3"]])
            region_iso_index_prod = region_iso_index_prod[region_iso_index_prod[0] == True].index
            timba_data_prod.loc[region_iso_index_prod, "Region"] = region

            try:
                region_iso_index_carbon = pd.DataFrame([x in region_iso for x in timba_data_carbon["ISO-Code"]])
                region_iso_index_carbon = region_iso_index_carbon[region_iso_index_carbon[0] == True].index
                timba_data_carbon.loc[region_iso_index_carbon, "Region"] = region
            except UnboundLocalError:
                pass

        timba_data_forest = timba_data_forest.groupby(
            ["Model", "Scenario", "Region", "year"])[["ForStock", "ForArea"]].sum().reset_index()

        timba_data_prod = timba_data_prod.groupby(
            ["Model", "Scenario", "Region", "year", "Commodity"])["quantity"].sum().reset_index()

        try:
            timba_data_carbon = timba_data_carbon.groupby(
                ["Model", "Scenario", "Region", "year"])["CarbonStockBiomass [MtCO2]"].sum().reset_index()
        except UnboundLocalError:
            pass

        # Add world
        timba_data_prod_world = timba_data_prod.groupby(
            ["Model", "Scenario", "year", "Commodity"])["quantity"].sum().reset_index()
        timba_data_prod_world["Region"] = "World"
        timba_data_prod = pd.concat([timba_data_prod, timba_data_prod_world], axis=0).reset_index(drop=True)

        timba_data_forest_world = timba_data_forest.groupby(
            ["Model", "Scenario", "year"])["ForStock", "ForArea"].sum().reset_index()
        timba_data_forest_world["Region"] = "World"
        timba_data_forest = pd.concat([timba_data_forest, timba_data_forest_world], axis=0).reset_index(drop=True)

        try:
            timba_data_carbon_world = timba_data_carbon.groupby(
                ["Model", "Scenario", "year"])["CarbonStockBiomass [MtCO2]"].sum().reset_index()
            timba_data_carbon_world["Region"] = "World"
            timba_data_carbon = pd.concat([timba_data_carbon, timba_data_carbon_world], axis=0).reset_index(drop=True)
        except UnboundLocalError:
            pass

        # Roundwood harvest (= industrial roundwood + other industrial roundwood) (in Mio m³)
        rnd_harvest = timba_data_prod[(timba_data_prod["Commodity"] == "Industrial Roundwood NC") |
                                      (timba_data_prod["Commodity"] == "Industrial Roundwood C") |
                                      (timba_data_prod["Commodity"] == "Other Industrial Roundwood")].reset_index(drop=True)
        rnd_harvest = rnd_harvest.groupby(["Model", "Scenario", "Region", "year"])["quantity"].sum().reset_index()
        rnd_harvest["quantity"] = rnd_harvest["quantity"] / 1000  # Conversion Tsd. to Mio m³
        rnd_harvest["Estimate"] = "Roundwood Harvest (Mm3/yr)"
        rnd_harvest = rnd_harvest.rename(columns={"quantity": "Data", "Scenario": "RCP-SSP", "year": "Year"})

        # Total harvest (roudwood harvest + fuelwood) (in Mio m³)
        total_harvest = timba_data_prod[(timba_data_prod["Commodity"] == "Fuelwood") |
                                        (timba_data_prod["Commodity"] == "Industrial Roundwood NC") |
                                        (timba_data_prod["Commodity"] == "Industrial Roundwood C") |
                                        (timba_data_prod["Commodity"] == "Other Industrial Roundwood")].reset_index(drop=True)
        total_harvest = total_harvest.groupby(["Model", "Scenario", "Region", "year"])["quantity"].sum().reset_index()
        total_harvest["quantity"] = total_harvest["quantity"] / 1000  # Conversion Tsd. to Mio m³
        total_harvest["Estimate"] = "Total Harvest (Mm3/yr)"
        total_harvest = total_harvest.rename(columns={"quantity": "Data", "Scenario": "RCP-SSP", "year": "Year"})

        # Forest area (Mha)
        forest_area = timba_data_forest[["Model", "Scenario", "Region", "year", "ForArea"]].copy()
        forest_area["ForArea"] = forest_area["ForArea"] / 1000
        forest_area["Estimate"] = "Forest Area (Mha)"
        forest_area = forest_area.rename(columns={"ForArea": "Data", "Scenario": "RCP-SSP", "year": "Year"})

        # Total forest non-soil C stock (MtC)
        try:
            carbon_biomass = timba_data_carbon[["Model", "Scenario", "Region", "year", "CarbonStockBiomass [MtCO2]"]].copy()
            carbon_biomass["CarbonStockBiomass [MtCO2]"] = carbon_biomass["CarbonStockBiomass [MtCO2]"] / (44 / 12)
            carbon_biomass["Model"] = "TiMBA"
            carbon_biomass["Estimate"] = "Total Forest Non-soil C Stock (MtC)"
            carbon_biomass = carbon_biomass.rename(
                columns={"CarbonStockBiomass [MtCO2]": "Data", "Scenario": "RCP-SSP", "year": "Year"})
        except UnboundLocalError:
            pass
        try:
            timba_data_new = pd.concat(
                [rnd_harvest, total_harvest, forest_area, carbon_biomass], axis=0).reset_index(drop=True)
        except UnboundLocalError:
            timba_data_new = pd.concat(
                [rnd_harvest, total_harvest, forest_area], axis=0).reset_index(drop=True)

        return timba_data_new

    def align_formip_data(self):
        """
        Alignes and merges TiMBA scenario results and FORMIP data.
        :return: Merged TiMBA and FORMIP data
        """
        formip_data = self.formip_data.copy()
        timba_data = self.timba_data.copy()

        year_structure_timba = timba_data["Year"].unique()

        formip_data = formip_data[
            [x in year_structure_timba for x in formip_data["Year"]]].reset_index(drop=True)

        formip_data = pd.concat([formip_data, timba_data], axis=0).reset_index(drop=True)

        formip_data = formip_data.rename(columns={"RCP-SSP" : "Scenario"})

        return formip_data

    def load_formip_data(self):
        self.formip_data = self.process_formip_data()
        self.timba_data = self.process_timba_data()
        self.formip_data = self.align_formip_data()
        return self.formip_data

class download_input_data:
    def __init__(self, 
                 SCENARIO_FOLDER_PATH: Path,
                 ADDINFOPATH: Path):
        self.SCENARIO_FOLDER_PATH = SCENARIO_FOLDER_PATH
        self.ADDINFOPATH = ADDINFOPATH

    def download_data_from_github(self):
        user = toolbox_paths.GIT_USER
        repo = toolbox_paths.GIT_REPO
        branch = toolbox_paths.GIT_BRANCH

        zip_url = f"https://github.com/{user}/{repo}/archive/refs/heads/{branch}.zip"

        folder_dict = {
            toolbox_paths.SCINPUT_GITHUB_URL: self.SCENARIO_FOLDER_PATH,
            toolbox_paths.AIINPUT_GITHUB_URL: self.ADDINFOPATH
        }

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)
                zip_path = tmpdir / f"{repo}.zip"

                print(f"Load {zip_url} ...")
                urllib.request.urlretrieve(zip_url, zip_path)

                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmpdir)

                repo_root = next(
                    p for p in tmpdir.iterdir()
                    if p.is_dir() and p.name.startswith(repo)
                )

                for source_rel, target_folder in folder_dict.items():
                    source_path = repo_root / source_rel

                    if not source_path.exists():
                        raise FileNotFoundError(
                            f"{source_rel} not found in {repo_root}"
                        )

                    if target_folder.exists():
                        print(f"{target_folder} already exists – skipping copy")
                        continue

                    target_folder.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(source_path, target_folder)

                    print(f"Input data saved to {target_folder}")

        except URLError:
            print(
                "Failed to download input data from GitHub.\n"
                "Please check your internet connection."
            )
