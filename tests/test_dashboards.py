import unittest
from pathlib import Path
from dash import Dash
from Toolbox.toolbox import timba_dashboard
import Toolbox.parameters.paths as toolbox_paths
from unittest.mock import patch, MagicMock
from Toolbox.parameters.defines import VarNames


class TestDashboardRouting(unittest.TestCase):

    def setUp(self):
        # ---- Patch _import_data COMPLETELY ----
        self.patcher_import_data = patch.object(
            timba_dashboard,
            "_import_data",
            autospec=True
        )
        self.mock_import_data = self.patcher_import_data.start()
        self.addCleanup(self.patcher_import_data.stop)

        # ---- Patch _import_formip COMPLETELY ----
        self.patcher_import_formip = patch.object(
            timba_dashboard,
            "_import_formip",
            autospec=True
        )
        self.mock_import_formip = self.patcher_import_formip.start()
        self.addCleanup(self.patcher_import_formip.stop)

        # ---- Instantiate dashboard ----
        self.dashboard = timba_dashboard(
            FOLDER_PATH=Path("example_path"),
            num_files_to_read=5,
            print_settings=False,
        )

        self.dashboard._app_initial()

        # ---- Inject fake data DIRECTLY ----
        self.dashboard.data = {
            VarNames.data_periods.value: {"dummy": 1}
        }
        self.dashboard.formip_data = {"formip": 1}

        self.dashboard._build_layout()
        self.dashboard._register_callbacks()

        cb = self.dashboard.app.callback_map["page-content.children"]
        self.display_page_callback = cb["callback"].__wrapped__


    # -------------------------
    #       TEST CASES
    # -------------------------

    def test_overview_page(self):
        result = self.display_page_callback("/")
        self.assertIs(result, self.dashboard.overview_db.app_layout)

    def test_forest_page(self):
        result = self.display_page_callback("/forest")
        self.assertIs(result, self.dashboard.forest_db.app_layout)

    def test_price_page(self):
        result = self.display_page_callback("/price")
        self.assertIs(result, self.dashboard.price_db.app_layout)

    def test_trade_page(self):
        result = self.display_page_callback("/trade")
        self.assertIs(result, self.dashboard.trade_db.app_layout)

    def test_validation_page(self):
        result = self.display_page_callback("/validation")
        self.assertIs(result, self.dashboard.validation_db.app_layout)

    def test_default_for_invalid_path(self):
        result = self.display_page_callback("/unknown-page")
        self.assertIs(result, self.dashboard.overview_db.app_layout)