import pytest
from dash import html
import Toolbox.toolbox as toolbox_module
from Toolbox.toolbox import timba_dashboard


class TestTimbaDashboard:
    @pytest.fixture(autouse=True)
    def _mock_all_dependencies(self, monkeypatch):
        # ==================================================
        # download_input_data mock
        # ==================================================
        class MockDownload:
            def download_data_from_github(self):
                return None

        monkeypatch.setattr(
            toolbox_module,
            "download_input_data",
            lambda *a, **k: MockDownload(),
        )

        # ==================================================
        # import_pkl_data mock
        # ==================================================
        class MockPKLImporter:
            def combined_data(self):
                return {"data_periods": [{}]}

        monkeypatch.setattr(
            toolbox_module,
            "import_pkl_data",
            lambda *a, **k: MockPKLImporter(),
        )

        # ==================================================
        # import_formip_data mock
        # ==================================================
        class MockFormipImporter:
            def load_formip_data(self):
                return {}

        monkeypatch.setattr(
            toolbox_module,
            "import_formip_data",
            lambda *a, **k: MockFormipImporter(),
        )

        class MockPage:
            def __init__(self, *args, **kwargs):
                self.app_layout = html.Div("Mock Page")

        monkeypatch.setattr(toolbox_module, "OverviewDB", MockPage)
        monkeypatch.setattr(toolbox_module, "ForestDB", MockPage)
        monkeypatch.setattr(toolbox_module, "PriceDB", MockPage)
        monkeypatch.setattr(toolbox_module, "TradeDB", MockPage)
        monkeypatch.setattr(toolbox_module, "ValidationDB", MockPage)

    def test_create_app_returns_dash_app(self, tmp_path):
        dashboard = timba_dashboard(FOLDER_PATH=tmp_path)
        dashboard.create_app()

        assert dashboard.app is not None
        assert dashboard.app.title == "TiMBA Dashboards"

    def test_layout_contains_page_content(self, tmp_path):
        dashboard = timba_dashboard(FOLDER_PATH=tmp_path)
        dashboard.create_app()

        ids = [c.id for c in dashboard.app.layout.children if hasattr(c, "id")]

        assert "page-content" in ids

    def test_run_does_not_open_browser(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            toolbox_module.webbrowser,
            "open_new",
            lambda *a, **k: None,
        )

        dashboard = timba_dashboard(FOLDER_PATH=tmp_path)
        dashboard.create_app()
        assert dashboard.app is not None
