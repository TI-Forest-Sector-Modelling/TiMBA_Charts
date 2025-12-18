import unittest
from pathlib import Path
from dash import Dash
from Toolbox.toolbox import timba_dashboard
import Toolbox.parameters.paths as toolbox_paths
from unittest.mock import patch, MagicMock
from Toolbox.parameters.defines import VarNames


class TestDashboardRouting(unittest.TestCase):

    def setUp(self):
        self.patcher_pkl = patch("Toolbox.classes.import_data.import_pkl_data")
        self.mock_pkl = self.patcher_pkl.start()

        self.patcher_formip = patch("Toolbox.classes.import_data.import_formip_data")
        self.mock_formip = self.patcher_formip.start()

        self.addCleanup(self.patcher_pkl.stop)
        self.addCleanup(self.patcher_formip.stop)

        # ---- Mock Data Returned by import_pkl_data ----
        mock_pkl_instance = MagicMock()
        mock_pkl_instance.combined_data.return_value = {
            VarNames.data_periods.value: {"dummy": 1}
        }
        self.mock_pkl.return_value = mock_pkl_instance

        # ---- Mock Data Returned by import_formip_data ----
        mock_formip_instance = MagicMock()
        mock_formip_instance.load_formip_data.return_value = {"formip": 1}
        self.mock_formip.return_value = mock_formip_instance

        # ---- Instantiate dashboard ----
        self.dashboard = timba_dashboard(
            FOLDER_PATH=Path("example_path"),
            num_files_to_read=5,
            print_settings=False,
        )

        self.dashboard._app_initial()
        self.dashboard._import_data()
        self.dashboard._import_formip()
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