import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import webbrowser
from threading import Timer
from pathlib import Path
from Toolbox.classes.import_data import import_pkl_data, import_formip_data, check_data_availability
from Toolbox.pages.overview_db import OverviewDB
from Toolbox.pages.forest_db import ForestDB
from Toolbox.pages.price_db import PriceDB
from Toolbox.pages.trade_db import TradeDB
from Toolbox.pages.validation_db import ValidationDB
from Toolbox.parameters.defines import VarNames
from Toolbox.classes.utils import generate_color_palette
from Toolbox.parameters.default_parameters import color_palette
import warnings


class timba_dashboard:

    def __init__(self,
                 scenario_folder_path: Path = None,
                 additional_info_folderpath: Path = None,
                 num_files_to_read: int = 10,
                 print_settings: bool = False):

        self.num_files_to_read = num_files_to_read
        self.scenario_folder_path = scenario_folder_path
        self.additional_info_folderpath = additional_info_folderpath
        self.print_settings = print_settings
        self.app = None
        self.data = None
        self.formip_data = None

    def run(self, open_browser=True, port=8053):
        self._app_initial()
        self._import_data()
        self._import_formip()
        self._build_layout()
        self._register_callbacks()

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
        check_data_availability(self,
                                sc_folder_path=self.scenario_folder_path,
                                additional_info_folder_path=self.additional_info_folderpath)
        importer = import_pkl_data(
            num_files_to_read=self.num_files_to_read,
            SCENARIOPATH=self.scenario_folder_path,
            ADDINFOPATH=self.additional_info_folderpath
        )
        self.data = importer.combined_data()

    def _import_formip(self):
        importer = import_formip_data(
            timba_data=self.data,
            only_baseline_sc=True,
            ADDINFOPATH=self.additional_info_folderpath
        )
        self.formip_data = importer.load_formip_data()

    def _build_layout(self):
        self.color_list = generate_color_palette(palette_name=color_palette, n_colors=self.num_files_to_read)
        self.overview_db = OverviewDB(app=self.app,
                                      data=self.data[VarNames.data_periods.value],
                                      print_settings=self.print_settings,
                                      color_list=self.color_list)
        self.forest_db = ForestDB(app=self.app,
                                  data=self.data[VarNames.data_periods.value],
                                  print_settings=self.print_settings,
                                  color_list=self.color_list)
        self.price_db = PriceDB(app=self.app,
                                data=self.data[VarNames.data_periods.value],
                                print_settings=self.print_settings,
                                color_list=self.color_list)
        self.trade_db = TradeDB(app=self.app,
                                data=self.data[VarNames.data_periods.value],
                                print_settings=self.print_settings,
                                color_list=self.color_list)
        self.validation_db = ValidationDB(app=self.app, data=self.formip_data)

        self.app.layout = dbc.Card([
            dcc.Location(id="url"),
            dbc.Navbar(
                dbc.Container([
                    dbc.Row([
                        dbc.Col(
                            dbc.Nav([], className="d-flex align-items-center"),
                            width=2
                        ),
                        dbc.Col(
                            dbc.NavbarBrand(
                                html.Img(
                                    src="https://raw.githubusercontent.com/TI-Forest-Sector-Modelling/TiMBA_Additional_Information/main/images/toolbox_assets/timba_dashboard_logo.png",
                                    height="80px"
                                ),
                                className="mx-auto"
                            ),
                            width=8,
                            className="d-flex justify-content-center align-items-center"
                        ),
                        dbc.Col(
                            dbc.Nav([
                                dbc.Button("Overview", href="/", color="primary", className="me-2"),
                                dbc.Button("Forest", href="/forest", color="success", className="me-2"),
                                dbc.Button("Price", href="/price", color="info", className="me-2"),
                                dbc.Button("Trade", href="/trade", color="warning", className="me-2"),
                                dbc.Button("Validation", href="/validation", color="secondary", className="me-2")
                            ], className="d-flex align-items-center ms-auto"),
                            width=2
                        ),
                    ], className="w-100 align-items-center")
                ]),
                color="light",
                dark=True,
                className="mb-2 border-3 rounded-4 shadow-sm",
                style={"height": "80px"}
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
    timba_dashboard(
        scenario_folder_path=None,
        additional_info_folderpath=None
        ).run()
