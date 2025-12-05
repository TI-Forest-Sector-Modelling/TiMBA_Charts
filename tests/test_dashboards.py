import unittest
from dash import Dash
from Toolbox.toolbox import timba_dashboard
import Toolbox.parameters.paths as toolbox_paths
from unittest.mock import patch, MagicMock
from Toolbox.parameters.defines import VarNames


class TestDashboardRouting(unittest.TestCase):
    @patch("Toolbox.classes.import_data.import_pkl_data")
    @patch("Toolbox.classes.import_data.import_formip_data")
    @patch("Toolbox.classes.import_data.check_data_availability")
    def setUp(self, mock_check, mock_formip, mock_pkl):
        """Prepare a dashboard instance with mocked data imports."""

        # ---- Mock Data Returned by import_pkl_data ----
        mock_pkl_instance = MagicMock()
        mock_pkl_instance.combined_data.return_value = {
            VarNames.data_periods.value: {"dummy": 1}
        }
        mock_pkl.return_value = mock_pkl_instance

        # ---- Mock Data Returned by import_formip_data ----
        mock_formip_instance = MagicMock()
        mock_formip_instance.load_formip_data.return_value = {"formip": 1}
        mock_formip.return_value = mock_formip_instance

        # ---- Instantiate dashboard ----
        self.dashboard = timba_dashboard(
            scenario_folder_path=None,
            additional_info_folderpath=None,
            num_files_to_read=5,
            print_settings=False,
        )

        # Manually run the setup steps
        self.dashboard._app_initial()
        self.dashboard._import_data()
        self.dashboard._import_formip()
        self.dashboard._build_layout()
        self.dashboard._register_callbacks()

        # Retrieve the Dash-managed callback
        cb = self.dashboard.app.callback_map["page-content.children"]
        wrapped_callback = cb["callback"]
        self.display_page_callback = wrapped_callback.__wrapped__

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