import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from Toolbox.toolbox import timba_dashboard
import Toolbox.parameters.default_parameters as dp


# Fixtures
@pytest.fixture
def dashboard_data():
    overview_df = pd.DataFrame({
        "Scenario": ["Baseline", "Alt1"],
        "Year": [2020, 2030],
        "Region": ["EU", "US"],
        "Model": ["TiMBA", "GLOBIOM"],
        "Estimate": ["Estimate1", "Estimate2"],
        "Value": [100, 200],
        "Data": [1.0, 2.0]
    })
    forest_df = overview_df.copy()
    pivot_map_data = pd.DataFrame({
        "ISO3": ["EU", "US"],
        "domain": ["Supply", "Demand"],
        "Baseline": [10, 20],
        "Alt1": [15, 25]
    })
    pivot_df_stock = pd.DataFrame({
        "ISO3": ["EU", "US"],
        "diff": [5, 5]
    })
    pivot_df_area = pd.DataFrame({
        "ISO3": ["EU", "US"],
        "diff": [100, 200]
    })
    formip_df = overview_df.copy()

    return overview_df, forest_df, pivot_map_data, pivot_df_stock, pivot_df_area, formip_df


# -----------------------------
# Tests
# -----------------------------
def test_build_layout(dashboard_data):
    overview_df, forest_df, pivot_map_data, pivot_df_stock, pivot_df_area, formip_df = dashboard_data
    dash_app = timba_dashboard()
    dash_app._app_initial()

    dash_app.data = {
        dp.overview_db: overview_df,
        dp.forest_db: forest_df
    }
    dash_app.pivot_map_data = pivot_map_data
    dash_app.pivot_df_stock = pivot_df_stock
    dash_app.pivot_df_area = pivot_df_area
    dash_app.formip_data = formip_df

    dash_app._build_layout()

    assert dash_app.overview_db.app_layout is not None
    assert dash_app.forest_db.app_layout is not None
    assert dash_app.validation_db.app_layout is not None
    assert dash_app.worldmap_db.app_layout is not None


def test_register_callbacks(dashboard_data):
    overview_df, forest_df, pivot_map_data, pivot_df_stock, pivot_df_area, formip_df = dashboard_data
    dash_app = timba_dashboard()
    dash_app._app_initial()
    dash_app.data = {
        dp.overview_db: overview_df,
        dp.forest_db: forest_df
    }
    dash_app.pivot_map_data = pivot_map_data
    dash_app.pivot_df_stock = pivot_df_stock
    dash_app.pivot_df_area = pivot_df_area
    dash_app.formip_data = formip_df

    dash_app._build_layout()
    dash_app._register_callbacks()

    assert dash_app.app is not None


def test_page_routing_callbacks_registered(dashboard_data):
    overview_df, forest_df, pivot_map_data, pivot_df_stock, pivot_df_area, formip_df = dashboard_data
    dash_app = timba_dashboard()
    dash_app._app_initial()
    dash_app.data = {
        dp.overview_db: overview_df,
        dp.forest_db: forest_df
    }
    dash_app.pivot_map_data = pivot_map_data
    dash_app.pivot_df_stock = pivot_df_stock
    dash_app.pivot_df_area = pivot_df_area
    dash_app.formip_data = formip_df

    dash_app._build_layout()
    dash_app._register_callbacks()

    callbacks = dash_app.app.callback_map
    assert "page-content.children" in callbacks