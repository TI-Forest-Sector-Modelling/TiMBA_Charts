import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import webbrowser
from threading import Timer
from pathlib import Path
from Toolbox.classes.import_data import import_pkl_data, import_formip_data
import Toolbox.parameters.paths as toolbox_paths
import warnings
from Toolbox.pages.overview_db import OverviewDB
from Toolbox.pages.forest_db import ForestDB
from Toolbox.pages.price_db import PriceDB
from Toolbox.pages.trade_db import TradeDB
from Toolbox.pages.validation_db import ValidationDB


app = dash.Dash(__name__, use_pages=False, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
app.title = "TiMBA Dashboards"
PACKAGEDIR = Path(__file__).parent.parent.absolute()

warnings.simplefilter(action='ignore', category=FutureWarning)
import_pkl = import_pkl_data(num_files_to_read=5,
                             SCENARIOPATH=toolbox_paths.SCINPUTPATH,
                             ADDINFOPATH=toolbox_paths.AIINPUTPATH)
data = import_pkl.combined_data()

import_formip_data = import_formip_data(timba_data=data,
                                        only_baseline_sc=True,
                                        ADDINFOPATH=toolbox_paths.AIINPUTPATH)
formip_data = import_formip_data.load_formip_data()

overview_db = OverviewDB(app=app, data=data["data_periods"], print_settings=False)
forest_db = ForestDB(app=app, data=data["data_periods"])
price_db = PriceDB(app=app, data=data["data_periods"])
trade_db = TradeDB(app=app, data=data["data_periods"])
validation_db = ValidationDB(app=app, data=formip_data)

app.layout = dbc.Card([
    dcc.Location(id="url"),
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
                            src="/assets/timba_dashboard_logo.png",
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
        className="mb-2 border-3 rounded-4 shadow-sm",
        style={"height": "80px"}
    ),
    html.Div(id="page-content"),
])


@app.callback(Output("page-content", "children"),
              Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/forest":
        return forest_db.app_layout
    elif pathname == "/price":
        return price_db.app_layout
    elif pathname == "/trade":
        return trade_db.app_layout
    elif pathname == "/validation":
        return validation_db.app_layout
    else:
        return overview_db.app_layout


if __name__ == "__main__":
    Timer(1, lambda: webbrowser.open_new("http://localhost:8053")).start()

    app.run(host='localhost', debug=False, dev_tools_ui=False, dev_tools_hot_reload=False, port=8053)
