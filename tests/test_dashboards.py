# import pytest
# import pandas as pd
# from dash import html
# import Toolbox.toolbox as toolbox_module
# from Toolbox.toolbox import timba_dashboard
# from pathlib import Path


# @pytest.fixture
# def mini_dataset():
#     base = Path("tests/test_data")

#     data_small = {
#         "overview_db": pd.read_pickle(base / "data_overview.pkl"),
#         "forest_db": pd.read_pickle(base / "data_forest.pkl"),
#     }

#     country_small = pd.read_pickle(base / "country.pkl")
#     commodity_small = pd.read_pickle(base / "commodity.pkl")
#     hist_small = pd.read_pickle(base / "hist.pkl")

#     return data_small, country_small, commodity_small, hist_small


# class TestTimbaDashboard:
#     @pytest.fixture(autouse=True)
#     def _mock_all_dependencies(self, monkeypatch):
#         # ==================================================
#         # download_input_data mock
#         # ==================================================
 
#         # --- Mock Download ---
#         class MockDownload:
#             def __init__(self, *args, **kwargs):
#                 pass

#             def download_data_from_github(self):
#                 return None

#         monkeypatch.setattr(
#             toolbox_module,
#             "download_input_data",
#             lambda *a, **k: MockDownload(),
#         )

#         # --- Mock Importer ---
#         class MockPKLImporter:
#             def __init__(self, *args, **kwargs):
#                 pass

#             def main(self):
#                 return mini_dataset

#         monkeypatch.setattr(
#             toolbox_module,
#             "import_pkl_data",
#             lambda *a, **k: MockPKLImporter(),
#         )

#         monkeypatch.setattr(
#             toolbox_module,
#             "import_pkl_data",
#             lambda *a, **k: MockPKLImporter(),
#         )

#         # ==================================================
#         # import_formip_data mock
#         # ==================================================
#         class MockFormipImporter:
#             def load_formip_data(self):
#                 return {}

#         monkeypatch.setattr(
#             toolbox_module,
#             "import_formip_data",
#             lambda *a, **k: MockFormipImporter(),
#         )

#         class MockPage:
#             def __init__(self, *args, **kwargs):
#                 self.app_layout = html.Div("Mock Page")

#         monkeypatch.setattr(toolbox_module, "OverviewDB", MockPage)
#         monkeypatch.setattr(toolbox_module, "ForestDB", MockPage)
#         monkeypatch.setattr(toolbox_module, "PriceDB", MockPage)
#         monkeypatch.setattr(toolbox_module, "BiTradeDB", MockPage)
#         monkeypatch.setattr(toolbox_module, "ValidationDB", MockPage)
#         monkeypatch.setattr(toolbox_module, "WorldMapDB", MockPage)

#     def test_create_app_returns_dash_app(self, tmp_path):
#         dashboard = timba_dashboard(FOLDER_PATH=tmp_path)
#         dashboard.create_app()

#         assert dashboard.app is not None
#         assert dashboard.app.title == "TiMBA Dashboards"

#     def test_layout_contains_page_content(self, tmp_path):
#         dashboard = timba_dashboard(FOLDER_PATH=tmp_path)
#         dashboard.create_app()

#         ids = [c.id for c in dashboard.app.layout.children if hasattr(c, "id")]

#         assert "page-content" in ids

#     def test_run_does_not_open_browser(self, tmp_path, monkeypatch):
#         monkeypatch.setattr(
#             toolbox_module.webbrowser,
#             "open_new",
#             lambda *a, **k: None,
#         )

#         dashboard = timba_dashboard(FOLDER_PATH=tmp_path)
#         dashboard.create_app()
#         assert dashboard.app is not None
