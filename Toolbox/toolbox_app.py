import dash
from dash import html
import dash_bootstrap_components as dbc
import webbrowser
from threading import Timer
from pathlib import Path
from Toolbox.classes.import_data import import_pkl_data
import Toolbox.parameters.paths as toolbox_paths
import warnings
from Toolbox.pages.overview_db import OverviewDB

app = dash.Dash(__name__, use_pages=False, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "TiMBA Dashboards"
PACKAGEDIR = Path(__file__).parent.parent.absolute()

warnings.simplefilter(action='ignore', category=FutureWarning)
import_pkl = import_pkl_data(num_files_to_read=5,
                             SCENARIOPATH=toolbox_paths.SCINPUTPATH,
                             ADDINFOPATH=toolbox_paths.AIINPUTPATH)
data = import_pkl.combined_data()

overview_db = OverviewDB(app=app, data=data["data_periods"], print_settings=False)

app.layout = dbc.Card([
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                # Left buttons
                dbc.Col(
                    dbc.Nav([
                        # dbc.Button("Data", href="/data", color="light", className="me-2")
                    ], className="d-flex align-items-center"),
                    width=2
                ),

                # Center logo
                dbc.Col(
                    dbc.NavbarBrand(
                        html.Img(
                            src="https://raw.githubusercontent.com/TI-Forest-Sector-Modelling/TiMBA/ToolBox_implementation_cm/images/timba_dashboard_logo.png",
                            height="80px"
                        ),
                        className="mx-auto"
                    ),
                    width=8,
                    className="d-flex justify-content-center align-items-center"
                ),

                # Right buttons
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
        className="mb-3 border-3 rounded-4 shadow-sm",
        style={"height": "80px"}
    ),

    overview_db.app_layout
])


if __name__ == "__main__":
    Timer(1, lambda: webbrowser.open_new("http://localhost:8052")).start()

    app.run(host='localhost', debug=False, dev_tools_ui=False, dev_tools_hot_reload=False, port=8052)
