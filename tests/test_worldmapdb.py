import pytest
import dash
import pandas as pd
import numpy as np

from Toolbox.pages.worldmap_db import WorldMapDB

# Fixtures
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "region": ["EU", "US"],
        "ISO3": ["DEU", "USA"],
        "domain": ["Supply", "Demand"],
        "year": [2030, 2030],
        "product": ["wood", "wood"],
        "unit": ["Mt", "Mt"],
        "Baseline": [10, 20],
        "ScenarioA": [15, 25],
    })


@pytest.fixture
def sample_stock():
    return pd.DataFrame({
        "ISO3": ["DEU", "USA"],
        "year": [2030, 2030],
        "Baseline": [100, 200],
        "ScenarioA": [110, 210],
    })


@pytest.fixture
def sample_area():
    return pd.DataFrame({
        "ISO3": ["DEU", "USA"],
        "year": [2030, 2030],
        "Baseline": [50, 60],
        "ScenarioA": [55, 70],
    })


@pytest.fixture
def dash_app():
    return dash.Dash(__name__)


@pytest.fixture
def worldmapdb_instance(dash_app, sample_data, sample_stock, sample_area):
    return WorldMapDB(
        app=dash_app,
        data=sample_data,
        df_stock=sample_stock,
        df_area=sample_area
    )

# Layout Tests
def test_layout_structure(worldmapdb_instance):
    layout = worldmapdb_instance.create_layout()
    assert layout is not None
    assert hasattr(layout, "children")
    assert len(layout.children) >= 3

# Callback registration
def test_callback_registered(worldmapdb_instance):
    callback_map = worldmapdb_instance.app.callback_map
    assert len(callback_map) > 0
    assert any(
        "wmdb_world_map_supply.figure" in key
        for key in callback_map.keys()
    )

# Callbacks output
def test_update_plots_callback(worldmapdb_instance):
    callback_map = worldmapdb_instance.app.callback_map
    callback_key = next(
        key for key in callback_map
        if "wmdb_world_map_supply.figure" in key
    )

    callback = callback_map[callback_key]
    assert "output" in callback

# Filtering
def test_filtering_logic():

    from Toolbox.classes.utils import PlotUtils

    df = pd.DataFrame({
        "region": ["EU", "US"],
        "year": [2030, 2040],
        "domain": ["Supply", "Demand"],
        "Baseline": [10, 20],
        "ScenarioA": [15, 25]
    })

    filtered = PlotUtils.filter_data(
        df=df,
        region=["EU"]
    )

    assert len(filtered) == 2
    assert filtered.iloc[0]["region"] == "EU"

# Scenario color test
def test_scenario_colors(worldmapdb_instance):

    colors = worldmapdb_instance.colors

    assert isinstance(colors, dict)