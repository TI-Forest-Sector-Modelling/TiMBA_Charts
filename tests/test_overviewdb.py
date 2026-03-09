import pytest
import pandas as pd
from dash import Dash
import dash_bootstrap_components as dbc

from Toolbox.pages.overview_db import OverviewDB
from Toolbox.classes.utils import PlotUtils
import Toolbox.parameters.default_parameters as dp

# Fixtures
@pytest.fixture
def sample_data():

    overview_df = pd.DataFrame({
        "Scenario": ["S1", "S2", "Historic Data"],
        "ISO3": ["DEU", "FRA", "DEU"],
        "Continent": ["Europe", "Europe", "Europe"],
        "Commodity": ["Wood", "Wood", "Wood"],
        "Commodity_Group": ["Forest", "Forest", "Forest"],
        "domain": ["Export", "Import", "Export"],
        "quantity": [10, 20, 5],
        "Value": [100, 200, 50],
        "Unit": ["t", "t", "t"],
        "Period": [1, 1, 1],
        "year": [2020, 2020, 2020]
    })

    forest_df = pd.DataFrame({
        "Scenario": ["S1", "S2"],
        "ISO3": ["DEU", "FRA"],
        "Continent": ["Europe", "Europe"],
        "ForArea": [100, 120],
        "ForStock": [200, 240],
        "Period": [1, 1],
        "year": [2020, 2020]
    })

    return {
        dp.overview_db: overview_df,
        dp.forest_db: forest_df
    }


@pytest.fixture
def colors():
    return {"S1": "#FF0000", "S2": "#00FF00", "Historic Data": "#0000FF"}


@pytest.fixture
def dashboard(sample_data, colors):
    app = Dash(__name__)
    return OverviewDB(app, sample_data, colors)

# Layout Tests
def test_layout_structure(dashboard):
    layout = dashboard.app_layout
    assert isinstance(layout, dbc.Container)
    assert len(layout.children) >= 3

    plot_container = layout.children[1]
    graph_cards = plot_container.children
    assert len(graph_cards) == 5

# detect sceanrios
def test_scenarios_detected(dashboard):

    assert "S1" in dashboard.scenarios
    assert "S2" in dashboard.scenarios

# Callbacks
def test_callbacks_registered(dashboard):
    app = dashboard.app
    assert len(app._callback_list) >= 2

# Filters
def test_filter_data_overview(sample_data):

    df = sample_data[dp.overview_db]

    filtered = PlotUtils.filter_data(
        df=df,
        scenario=["S1"]
    )

    assert len(filtered) == 1
    assert filtered.iloc[0]["Scenario"] == "S1"

# CSV download
def test_csv_generation(sample_data):
    df = sample_data[dp.overview_db]
    csv = df.to_csv(index=False)
    assert "Scenario" in csv
    assert "Historic Data" in csv