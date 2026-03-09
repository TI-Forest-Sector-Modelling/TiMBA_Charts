import pytest
import pandas as pd
from dash import Dash
import dash_bootstrap_components as dbc

from Toolbox.pages.forest_db import ForestDB
from Toolbox.classes.utils import PlotUtils


# Fixtures
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Scenario": ["S1", "S2"],
        "ISO3": ["DEU", "FRA"],
        "Continent": ["Europe", "Europe"],
        "ForArea": [100, 120],
        "ForStock": [200, 250],
        "supply_from_forest": [50, 60],
        "Period": [1, 1],
        "year": [2020, 2020]
    })


@pytest.fixture
def colors():
    return {"S1": "#FF0000", "S2": "#00FF00"}


@pytest.fixture
def dashboard(sample_data, colors):
    app = Dash(__name__)
    return ForestDB(app, sample_data, colors)

# Layout tests
def test_layout_structure(dashboard):
    layout = dashboard.app_layout
    assert isinstance(layout, dbc.Container)
    assert len(layout.children) >= 3

    plot_container = layout.children[1]
    graph_cards = plot_container.children
    assert len(graph_cards) == 8


# Detect sceanrios
def test_scenarios_detected(dashboard):
    assert dashboard.scenarios == ["S1", "S2"]


# Callbacks
def test_callbacks_registered(dashboard):

    app = dashboard.app
    assert len(app._callback_list) >= 2

# Filters
def test_filter_data():

    df = pd.DataFrame({
        "Scenario": ["S1", "S2"],
        "ISO3": ["DEU", "FRA"]
    })

    filtered = PlotUtils.filter_data(
        df=df,
        scenario=["S1"]
    )

    assert len(filtered) == 1
    assert filtered.iloc[0]["Scenario"] == "S1"

# CSV download
def test_csv_generation(sample_data):

    csv = sample_data.to_csv(index=False)

    assert "Scenario" in csv
    assert "S1" in csv