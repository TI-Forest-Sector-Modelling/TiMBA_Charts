import click
import warnings
from Toolbox.toolbox import timba_dashboard
import Toolbox.parameters.paths as toolbox_paths
from pathlib import Path
warnings.simplefilter(action='ignore', category=FutureWarning)

@click.group()
def cli():
    pass

#Dashboard Command
@click.command()
@click.option('-NF', '--num_files', default=10, 
              show_default=True, required=True, type=int, 
              help="Number of .pkl files to read")
@click.option('-FP', '--sc_folderpath', default=None,
              show_default=True, required=True, type=Path, 
              help="Define the folder where the code will look for .pkl files containing the scenarios.")
@click.option('-AIFP', '--additional_info_folderpath', default=None,
              show_default=True, required=True, type=Path, 
              help="Define the folder where the code will look for additional infos, like historic data or country information.")
@click.option('-PS', '--print_settings', default=False, 
              show_default=True, required=True, type=bool, 
              help="If True, the quantity plot will be plotted with bigger lines and font sizes, so that the figure can be used for presentations etc.")

def dashboard_cli(num_files,sc_folderpath,additional_info_folderpath,print_settings):    
    td = timba_dashboard(num_files_to_read=num_files,
                         scenario_folder_path=sc_folderpath,
                         additional_info_folderpath=additional_info_folderpath,
                         print_settings=print_settings)
    td.run()

cli.add_command(dashboard_cli, name="dashboard")

