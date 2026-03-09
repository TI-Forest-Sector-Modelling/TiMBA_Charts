import pytest
import dash
import pandas as pd
import plotly.graph_objects as go

from Toolbox.pages.validation_db import ValidationDB


# Fixtures
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Region": ["EU", "EU", "US", "US"],
        "Estimate": ["Demand", "Demand", "Demand", "Demand"],
        "Scenario": ["SSP1", "SSP2", "SSP1", "SSP2"],
        "Model": ["TiMBA", "GFPM", "GLOBIOM", "TiMBA"],
        "Year": [2020, 2030, 2020, 2030],
        "Data": [100, 110, 120, 130]
    })


@pytest.fixture
def dash_app():
    return dash.Dash(__name__)


@pytest.fixture
def validationdb_instance(dash_app, sample_data):
    return ValidationDB(
        app=dash_app,
        data=sample_data,
        print_settings=False
    )

# Initialization Test
def test_initialization(validationdb_instance):
    assert validationdb_instance.start == 2020
    assert validationdb_instance.end == 2030
    assert isinstance(validationdb_instance.model_colors, dict)

# Layout
def test_layout_structure(validationdb_instance):
    layout = validationdb_instance.create_layout()
    assert layout is not None
    assert hasattr(layout, "children")
    assert len(layout.children) >= 2

# Callbacks
def test_callbacks_registered(validationdb_instance):
    callback_map = validationdb_instance.app.callback_map
    assert len(callback_map) >= 2
    assert any(
        "vdb_formip-plot.figure" in key
        for key in callback_map.keys()
    )


# Filters
def test_filter_data(validationdb_instance):
    filtered = validationdb_instance.filter_data(
        region=["EU"],
        estimate=["Demand"],
        scenario=["SSP1"],
        model=["TiMBA"]
    )
    assert len(filtered) == 1
    assert filtered.iloc[0]["Region"] == "EU"
    assert filtered.iloc[0]["Model"] == "TiMBA"

# Plot Function Tests
def test_plot_ssp_fsm_range(validationdb_instance, sample_data):
    fig = validationdb_instance.plot_ssp_fsm_range(sample_data)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_plot_ssp_fsm_all(validationdb_instance, sample_data):
    fig = validationdb_instance.plot_ssp_fsm_all(sample_data)
    assert isinstance(fig, go.Figure)

# Bar Plot
def test_bar_plot_fsm(validationdb_instance, sample_data):
    fig = validationdb_instance.bar_plot_fsm(
        data=sample_data,
        value_type="absolute values",
        start_year=2020,
        end_year=2030
    )
    assert isinstance(fig, go.Figure)

# Update Plot Validation
def test_update_plot_validation(validationdb_instance):
    fig1, fig2 = validationdb_instance.update_plot_validation(
        region=["EU"],
        estimate=["Demand"],
        scenario=["SSP1"],
        model=["TiMBA"],
        figure_type="ssp_fsm_range",
        value_type="relative values",
        start_year=2020,
        end_year=2030
    )
    assert isinstance(fig1, go.Figure)
    assert isinstance(fig2, go.Figure)

# Title generation
def test_generate_title(validationdb_instance):

    title = validationdb_instance.generate_title(
        region=["EU"],
        estimate=["Demand"],
        scenario=["SSP1"],
        model=["TiMBA"],
        plot="plot",
        value_type="relative values"
    )

    assert "EU" in title
    assert "SSP1" in title