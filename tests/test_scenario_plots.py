import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from Toolbox.classes.PlotManager import Plots


# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Scenario": ["S1", "S1", "S2", "S2"],
        "year": [2020, 2025, 2020, 2025],
        "Period": [1, 2, 1, 2],
        "quantity": [1000, 2000, 1500, 2500],
        "Value": [1000000, 2000000, 1200000, 2400000],
        "ForArea": [10000, 11000, 10500, 11500],
        "ForStock": [50000, 55000, 52000, 58000],
        "supply_from_forest": [1000, 1200, 1100, 1300],
        "domain": ["Net Exports", "Manufacturing", "Net Exports", "Demand"],
        "ISO3": ["DEU", "DEU", "FRA", "FRA"],
        "diff": [10, -5, 3, -2],
    })


@pytest.fixture
def colors():
    return {"S1": "blue", "S2": "green"}


@pytest.fixture
def plots():
    return Plots()


# -----------------------------
# Generic Helper
# -----------------------------

def assert_basic_figure_properties(fig):
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0
    assert fig.layout.template is not None


# -----------------------------
# Tests
# -----------------------------

def test_create_quantity_plot(sample_df, colors, plots):
    fig = plots.create_quantity_plot(sample_df, colors, "Test", "m³")
    assert_basic_figure_properties(fig)
    assert all(isinstance(t, go.Scatter) for t in fig.data)
    assert "Quantity" in fig.layout.title.text


def test_create_value_plot(sample_df, colors, plots):
    fig = plots.create_value_plot(sample_df, colors, "Test")
    assert_basic_figure_properties(fig)
    assert all(isinstance(t, go.Scatter) for t in fig.data)
    assert "Value" in fig.layout.title.text


def test_create_value_growth_plot(sample_df, colors, plots):
    fig = plots.create_value_growth_plot(sample_df, colors, "Test")
    assert_basic_figure_properties(fig)
    assert all(isinstance(t, go.Bar) for t in fig.data)


def test_create_price_plot(sample_df, colors, plots):
    fig = plots.create_price_plot(sample_df, colors, "Test")
    assert_basic_figure_properties(fig)


def test_create_price_growth_plot(sample_df, colors, plots):
    fig = plots.create_price_growth_plot(sample_df, colors, "Test")
    assert_basic_figure_properties(fig)


def test_create_trade_line_plot(sample_df, colors, plots):
    fig = plots.create_trade_line_plot(
        sample_df,
        trade_domain="Net Exports",
        unit="quantity",
        colors=colors,
        title="Test",
        y_label="m³"
    )
    assert_basic_figure_properties(fig)


def test_create_trade_bar_plot(sample_df, colors, plots):
    fig = plots.create_trade_bar_plot(
        sample_df,
        trade_domain="Net Exports",
        unit="quantity",
        colors=colors,
        title="Test",
        y_label="m³"
    )
    assert_basic_figure_properties(fig)


def test_create_world_map_plot(sample_df, plots):
    fig = plots.create_world_map_plot(
        sample_df,
        max_year=2025,
        title="Test",
        colorbar_label="m³"
    )
    assert_basic_figure_properties(fig)


def test_create_diff_world_map_plot(sample_df, plots):
    fig = plots.create_diff_world_map_plot(sample_df, "Diff Test")
    assert_basic_figure_properties(fig)


def test_plot_forarea(sample_df, colors, plots):
    fig = plots.plot_forarea(sample_df, colors, "Test")
    assert_basic_figure_properties(fig)


def test_plot_forstock(sample_df, colors, plots):
    fig = plots.plot_forstock(sample_df, colors, "Test")
    assert_basic_figure_properties(fig)


def test_plot_forest_growth(sample_df, colors, plots):
    fig = plots.plot_forest_growth(sample_df, colors, "Test", domain="ForArea")
    assert_basic_figure_properties(fig)


def test_plot_nai(sample_df, colors, plots):
    fig = plots.plot_nai(sample_df, colors, calc="nai", title="Test")
    assert_basic_figure_properties(fig)


def test_plot_stock_area_ratio(sample_df, colors, plots):
    fig = plots.plot_stock_area_ratio(sample_df, colors, "Test")
    assert_basic_figure_properties(fig)


def test_plot_supply_from_forest(sample_df, colors, plots):
    fig = plots.plot_supply_from_forest(sample_df, colors, "Test")
    assert_basic_figure_properties(fig)