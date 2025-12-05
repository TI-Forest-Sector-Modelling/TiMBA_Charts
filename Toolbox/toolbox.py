from Toolbox.classes.import_data import import_pkl_data
from Toolbox.classes.dashboard import DashboardPlotter
from Toolbox.classes.validation_db import Vali_DashboardPlotter
from pathlib import Path
import Toolbox.parameters.paths as toolbox_paths

class timba_dashboard:
    def __init__(self,scenario_folder_path:Path,
                 additional_info_folderpath:Path,
                 num_files_to_read:int=10,
                 print_settings:bool=False):
        self.num_files_to_read = num_files_to_read
        self.scenario_folder_path = scenario_folder_path
        self.additional_info_folderpath = additional_info_folderpath
        self.print_settings = print_settings

    def import_data(self):
        import warnings
        warnings.simplefilter(action='ignore', category=FutureWarning)
        import_pkl = import_pkl_data(num_files_to_read=self.num_files_to_read,
                                     SCENARIOPATH=self.scenario_folder_path,
                                     ADDINFOPATH=self.additional_info_folderpath)
        self.data = import_pkl.combined_data()

    def call_dashboard(self):
        DashboardPlotter(data=self.data["data_periods"],print_settings=self.print_settings).run()

    def run(self):
        self.import_data()
        self.call_dashboard() 

# class bilateral_trade_dashboard:
#     def __init__(self,scenario_folder_path:Path,
#                  num_files_to_read:int=10):
#         self.num_files_to_read = num_files_to_read
#         self.scenario_folder_path = scenario_folder_path

#     def import_data(self):
#         import warnings
#         warnings.simplefilter(action='ignore', category=FutureWarning)
#         import_pkl = import_pkl_data(num_files_to_read=self.num_files_to_read,
#                                      SCENARIOPATH=self.scenario_folder_path)
#         self.data = import_pkl.combined_data()

#     def call_dashboard(self):
#         BT_DashboardPlotter(data=self.data["data_periods"]).run()

#     def run(self):
#         self.import_data()
#         self.call_dashboard() 

class validation_dashboard:
    def __init__(self,
                 scenario_folder_path:Path,
                 additional_info_folderpath:Path,
                 num_files_to_read:int=10,
                 only_baseline_sc:bool=True):
        self.num_files_to_read = num_files_to_read
        self.scenario_folder_path = scenario_folder_path
        self.additional_info_folderpath = additional_info_folderpath
        self.only_baseline_sc = only_baseline_sc

    def import_data(self):
        import warnings
        warnings.simplefilter(action='ignore', category=FutureWarning)
        from Toolbox.classes.import_data import import_pkl_data, import_formip_data
        import_pkl = import_pkl_data(num_files_to_read=self.num_files_to_read,
                                     ADDINFOPATH=self.additional_info_folderpath,
                                     SCENARIOPATH=self.scenario_folder_path)
        self.data = import_pkl.combined_data()

        import_formip_data = import_formip_data(timba_data=self.data, 
                                                only_baseline_sc=self.only_baseline_sc,
                                                ADDINFOPATH=self.additional_info_folderpath)
        self.formip_data = import_formip_data.load_formip_data()


    def call_dashboard(self):
        Vali_DashboardPlotter(data=self.formip_data).run()

    def run(self):
        self.import_data()
        self.call_dashboard() 

if __name__ == "__main__":
    td = timba_dashboard(num_files_to_read=4,
                         scenario_folder_path=toolbox_paths.SCINPUTPATH,
                         additional_info_folderpath= toolbox_paths.AIINPUTPATH,
                         print_settings=False)
    td.run()

    # vd = validation_dashboard(num_files_to_read=5,
    #                           scenario_folder_path=toolbox_paths.SCINPUTPATH,
    #                           additional_info_folderpath=toolbox_paths.AIINPUTPATH)
    # vd.run()