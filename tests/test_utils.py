import pytest
import pandas as pd
import numpy as np
from Toolbox.classes.utils import PlotUtils
from Toolbox.parameters.filter_config import PLOT_FILTERS

def test_generate_color_palette():
    palette = PlotUtils.generate_color_palette("D3", 5)
    assert isinstance(palette, list)
    assert len(palette) == 5

def test_get_scenario_colors():
    scenarios = ["S1", "S2", "S3"]
    colors = PlotUtils.get_scenario_colors(scenarios, "D3")
    assert isinstance(colors, dict)
    assert set(colors.keys()) == set(scenarios)
    assert all(isinstance(v, str) for v in colors.values())

# Test dynamic_y_range
def test_dynamic_y_range():
    vals = [10, 20, 30]
    y_range = PlotUtils.dynamic_y_range(vals, 0.8, 1.2)
    assert y_range[0] == 10 * 0.8
    assert y_range[1] == 30 * 1.2
    assert PlotUtils.dynamic_y_range([]) is None

# Test filter_data
def test_filter_data():
    df = pd.DataFrame({
        "ISO3": ["R1","R2","R3"],
        "Continent": ["EU","AS","AF"],
        "domain": ["Supply","Consumption","Export"]
    })
    filtered = PlotUtils.filter_data(df, region=["R1"], continent=["EU"])
    assert len(filtered) == 1
    assert filtered.iloc[0]["ISO3"] == "R1"

# Test generate_title
def test_generate_title():
    filt = {"Region": ["R1","R2"], "Scenario": "S1"}
    title = PlotUtils.generate_title(filt)
    assert "R1" in title and "S1" in title
    title_ignore = PlotUtils.generate_title(filt, ignore_keys=["Scenario"])
    assert "S1" not in title_ignore

# Test remove_extreme_outliers
def test_remove_extreme_outliers():
    df = pd.DataFrame({"val": [1,2,3,1000]})
    df_clean = PlotUtils.remove_extreme_outliers(df.copy(), "val", threshold=1)
    assert np.isnan(df_clean["val"].iloc[-1])
    assert df_clean["val"].iloc[0] == 1

# Test build_filter_inputs
def test_build_filter_inputs():
    inputs = PlotUtils.build_filter_inputs("prefix", {"key1": {}, "key2": {}})
    from dash.dependencies import Input
    assert all(isinstance(i, Input) for i in inputs)
    assert len(inputs) == 2

# # Test get_plot_filters
# def test_get_plot_filters(monkeypatch):
#     plot_name = "test_plot"
#     monkeypatch.setattr("Toolbox.parameters.filter_config.PLOT_FILTERS", {plot_name:["Region","Scenario"]})
    
#     filt_vals = {"Region":["R1"], "Scenario":"S1", "domain":"Supply"}
#     out = PlotUtils.get_plot_filters(filt_vals, plot_name)
#     assert set(out.keys()) == {"Region","Scenario"}

# Test dynamic_y_label
def test_dynamic_y_label():
    df = pd.DataFrame({"Unit":["t","m3","t"]})
    label = PlotUtils.dynamic_y_label(df)
    assert "t" in label and "m3" in label