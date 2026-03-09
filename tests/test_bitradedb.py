import pytest
import pandas as pd
from dash import Dash
import dash_bootstrap_components as dbc
import dash

from Toolbox.pages.bitrade_db import BiTradeDB
from Toolbox.classes.utils import PlotUtils


# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Scenario": ["S1", "S2"],
        "ISO3": ["R1", "R2"],
        "Continent": ["EU", "AS"],
        "domain": ["Import", "Export"],
        "Commodity": ["Wood", "Wood"],
        "Commodity_Group": ["Forest", "Forest"],
        "quantity": [10, 20],
        "Unit": ["t", "t"],
        "Value": [100, 200],
        "year": [2020, 2020]
    })


@pytest.fixture
def colors():
    return {"S1": "#FF0000", "S2": "#00FF00"}


@pytest.fixture
def dashboard(sample_data, colors):
    app = Dash(__name__)
    return BiTradeDB(app, sample_data, colors)


# -------------------------
# Layout Tests
# -------------------------
def test_layout_structure(dashboard):

    layout = dashboard.app_layout

    # Hauptcontainer
    assert isinstance(layout, dbc.Container)

    # Filtercard existiert
    assert len(layout.children) >= 3

    filter_card = layout.children[0]
    assert hasattr(filter_card, "children")

    # Plot container
    plot_container = layout.children[1]
    graph_cards = plot_container.children

    # 6 Graphkarten erwartet
    assert len(graph_cards) == 6


# -------------------------
# Callbacks
# -------------------------
def test_callbacks_registered(dashboard):

    app = dashboard.app
    assert len(app._callback_list) >= 2


# -------------------------
# Filter
# -------------------------
def test_filtering_logic(sample_data):

    filtered = PlotUtils.filter_data(
        df=sample_data,
        scenario=["S1"]
    )

    assert len(filtered) == 1
    assert filtered.iloc[0]["Scenario"] == "S1"


# -------------------------
# CSV Download
# -------------------------
def test_download_logic(sample_data):

    filtered = PlotUtils.filter_data(
        df=sample_data,
        scenario=["S1"]
    )

    csv = filtered.to_csv(index=False)

    assert "Scenario" in csv
    assert "S1" in csv