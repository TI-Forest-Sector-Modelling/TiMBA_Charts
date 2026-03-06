# # tests/test_bitradedb.py
# import pytest
# import pandas as pd
# from dash import Dash
# import dash
# from Toolbox.pages.bitrade_db import BiTradeDB

# # -------------------------
# # Fixtures
# # -------------------------
# @pytest.fixture
# def sample_data():
#     return pd.DataFrame({
#         "Scenario": ["S1", "S2"],
#         "ISO3": ["R1", "R2"],
#         "Continent": ["EU", "AS"],
#         "domain": ["Import", "Export"],
#         "Commodity": ["Wood", "Wood"],
#         "Commodity_Group": ["Forest", "Forest"],
#         "quantity": [10, 20],
#         "Unit": ["t", "t"],
#         "Value": [100, 200]
#     })

# @pytest.fixture
# def colors():
#     return {"S1": "#FF0000", "S2": "#00FF00"}

# @pytest.fixture
# def dash_app(sample_data, colors):
#     app = Dash(__name__)
#     dashboard = BiTradeDB(app, sample_data, colors)
#     return dashboard

# # -------------------------
# # Test Layout
# # -------------------------
# def test_layout_structure(dash_app):
#     layout = dash_app.app_layout
#     # Container vorhanden
#     assert layout.type == "Container"
#     # Filter-Card existiert
#     filter_card = layout.children[0]
#     assert "children" in filter_card.to_plotly_json()
#     # Mindestens 6 Graph-Karten existieren
#     graph_cards = layout.children[1].children
#     assert len(graph_cards) == 6
#     assert all(hasattr(card, "children") or getattr(card, "type", None) == "Graph" for card in graph_cards)
#     # Download-Element existiert
#     download_elem = layout.children[-1]
#     assert download_elem.id == "tdb_download"

# # -------------------------
# # Test Plot Callbacks
# # -------------------------
# def test_update_plots_callback(dash_app, sample_data, colors):
#     callback_id = "tbd_import_q.figure"
#     assert callback_id in dash_app.app.callback_map
#     cb_func = dash_app.app.callback_map[callback_id]["callback"]
#     # Dummy filter values (alle None)
#     filter_values = [None] * len(dash_app.filters)
#     figs = cb_func(*filter_values)
#     # Prüfe, dass 6 Figuren zurückkommen
#     assert len(figs) == 6
#     # Alle Figuren sind dicts (Plotly Figures)
#     assert all(isinstance(f, dict) for f in figs)

# # -------------------------
# # Test CSV Download Callback
# # -------------------------
# def test_download_csv_callback(dash_app):
#     callback_id = "tdb_download.data"
#     assert callback_id in dash_app.app.callback_map
#     cb_func = dash_app.app.callback_map[callback_id]["callback"]
    
#     # Kein Klick -> dash.no_update
#     out = cb_func(None, *([None]*len(dash_app.filters)))
#     assert out == dash.no_update

#     # Klick simulieren -> CSV zurück
#     out = cb_func(1, *([None]*len(dash_app.filters)))
#     assert isinstance(out, dict)
#     assert "content" in out  # CSV wird als content zurückgegeben

# # -------------------------
# # Test Szenario-Filter Logik
# # -------------------------
# def test_filtering_logic(dash_app):
#     from Toolbox.classes.utils import PlotUtils
#     filt_dict = {"Scenario": ["S1"]}
#     filtered = PlotUtils.filter_data(dash_app.data, **filt_dict)
#     assert all(filtered["Scenario"] == "S1")