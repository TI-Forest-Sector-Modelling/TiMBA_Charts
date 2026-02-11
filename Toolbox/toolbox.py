import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import webbrowser
from threading import Timer
from pathlib import Path
from Toolbox.classes.InputManager import import_pkl_data, import_formip_data, download_input_data
from Toolbox.classes.ProcessManager import DataProcessor
from Toolbox.pages.overview_db import OverviewDB
from Toolbox.pages.forest_db import ForestDB
from Toolbox.pages.price_db import PriceDB
from Toolbox.pages.trade_db import TradeDB
from Toolbox.pages.validation_db import ValidationDB
from Toolbox.classes.utils import PlotUtils
import Toolbox.parameters.default_parameters as dp
from Toolbox.parameters.paths import PACKAGEDIR,SCINPUTPATH,AIINPUTPATH,SCFOLDERPATH
import warnings


class timba_dashboard:

    def __init__(self,
                 FOLDER_PATH: Path = PACKAGEDIR,
                 num_files_to_read: int = 10,
                 print_settings: bool = False):

        self.num_files_to_read = num_files_to_read
        self.SCENARIO_PATH = FOLDER_PATH / SCFOLDERPATH / SCINPUTPATH
        self.ADDINFO_PATH = FOLDER_PATH / SCFOLDERPATH / AIINPUTPATH
        self.FOLDER_PATH = FOLDER_PATH
        self.print_settings = print_settings
        self.app = None
        self.data = None
        self.formip_data = None

    def create_app(self):
        self._app_initial()
        self._import_data()
        self._import_formip()
        self._build_layout()
        self._register_callbacks()
        return self.app
    
    def run(self, open_browser=True, port=8053):
        self.create_app()

        if open_browser:
            Timer(1, lambda: webbrowser.open_new(f"http://localhost:{port}")).start()

        self.app.run(
            host="localhost",
            port=port,
            debug=False,
            dev_tools_ui=False,
            dev_tools_hot_reload=False
        )

    def _app_initial(self):
        self.app = dash.Dash(
            __name__,
            use_pages=False,
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        self.app.title = "TiMBA Dashboards"
        self.app.config.suppress_callback_exceptions = True

    def _import_data(self):
        warnings.simplefilter(action='ignore', category=FutureWarning)

        if not (self.SCENARIO_PATH.exists() and self.ADDINFO_PATH.exists()):
            print(f"No data found at: {self.FOLDER_PATH}")
            print("\nStart input data download:")
            download = download_input_data(SCENARIO_FOLDER_PATH=self.SCENARIO_PATH,
                                           ADDINFOPATH=self.ADDINFO_PATH)
            download.download_data_from_github()

        print("\nStart the read-in process of TiMBA data")
        importer = import_pkl_data(
            num_files_to_read=self.num_files_to_read,
            SCENARIOPATH=self.SCENARIO_PATH,
            ADDINFOPATH=self.ADDINFO_PATH
        )
        data, country_data, commodity_data, hist_data = importer.main()
        process = DataProcessor(data=data,country_data=country_data,
                                commodity_data=commodity_data,
                                data_hist=hist_data)
        self.data = process.combined_data()
        print("TiMBA data is fully loaded!")

    def _import_formip(self):
        importer = import_formip_data(
            timba_data=self.data,
            only_baseline_sc=True,
            ADDINFOPATH=self.ADDINFO_PATH
        )
        self.formip_data = importer.load_formip_data()

    def _build_layout(self):
        #self.color_list = PlotUtils.generate_color_palette(palette_name=dp.color_palette, n_colors=self.num_files_to_read)
        self.overview_db = OverviewDB(app=self.app,
                                      data=self.data,
                                      print_settings=self.print_settings,
                                      #color_list=self.color_list,
                                      )
        self.forest_db = ForestDB(app=self.app,
                                  data=self.data[dp.forest_db],
                                  #print_settings=self.print_settings,
                                  #color_list=self.color_list,
                                  )
        self.price_db = PriceDB(app=self.app,
                                data=self.data[dp.overview_db],
                                #print_settings=self.print_settings,
                                #color_list=self.color_list,
                                )
        self.trade_db = TradeDB(app=self.app,
                                data=self.data[dp.overview_db],
                                print_settings=self.print_settings,
                                #color_list=self.color_list,
                                )
        self.validation_db = ValidationDB(app=self.app, data=self.formip_data)

        self.app.layout = dbc.Card([
            dcc.Location(id="url"),
            dbc.Navbar(
                dbc.Container(
                    dbc.Col(
                        [
                            # Logo oben
                            dbc.NavbarBrand(
                                html.Img(
                                    src=dp.logo,
                                    height="80px",
                                    style={"mixBlendMode": "multiply"}
                                ),
                                className="mx-auto"
                            ),

                            # Tabs darunter
                            dbc.Nav(
                                [
                                    dbc.NavLink("Overview", href="/", active="exact"),
                                    dbc.NavLink("Forest", href="/forest", active="exact"),
                                    dbc.NavLink("Price", href="/price", active="exact"),
                                    dbc.NavLink("Trade", href="/trade", active="exact"),
                                    dbc.NavLink("Validation", href="/validation", active="exact")
                                ],
                                navbar=True,
                                className="tabs-equal justify-content-center mt-2"
                            )
                        ],
                        width=12,
                        className="d-flex flex-column align-items-center"
                    )
                ),
                color="light",
                dark=False,
                className="mb-2 border-3 rounded-4 shadow-sm",
                style={"height": "140px"}  # passt für Logo + Tabs
            ),
            html.Div(id="page-content"),
        ])


    def _register_callbacks(self):

        @self.app.callback(
            Output("page-content", "children"),
            Input("url", "pathname")
        )
        def _display_page(pathname):
            if pathname == "/forest":
                return self.forest_db.app_layout
            elif pathname == "/price":
                return self.price_db.app_layout
            elif pathname == "/trade":
                return self.trade_db.app_layout
            elif pathname == "/validation":
                return self.validation_db.app_layout
            return self.overview_db.app_layout


if __name__ == "__main__":
    timba_dashboard().run()
