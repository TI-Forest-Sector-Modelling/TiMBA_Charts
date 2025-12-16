# import pytest
# import pandas as pd
# from unittest.mock import patch, mock_open
# import pickle
# import gzip
# from pathlib import Path
# from io import BytesIO
# from Toolbox.classes.scenario_plots import PlotDropDown, sc_plot
# import Toolbox.parameters.paths as toolbox_paths
# import Toolbox.parameters.default_parameters as toolbox_parameters

# @pytest.fixture
# def sample_data():
#     return pd.DataFrame({
#         'year': [2000, 2001, 2002, 2000, 2001, 2002],
#         'Scenario': ['A', 'A', 'A', 'B', 'B', 'B'],
#         'quantity': [10, 20, 30, 15, 25, 35],
#         'RegionCode': ['R1'] * 6,
#         'Continent': ['Europe'] * 6,
#         'Model': ['M1'] * 6,
#         'domain': ['Dom1'] * 6,
#         'CommodityCode': ['C1'] * 6,
#     })

# def test_predefined_plot_runs_without_error(sample_data):
#     plot_instance = sc_plot()
#     try:
#         plot_instance.predefined_plot(sample_data)
#     except Exception as e:
#         pytest.fail(f"predefined_plot() raised an exception: {e}")

# def test_plot_dropdown_initialization(sample_data):
#     try:
#         dropdown = PlotDropDown(sample_data)
#         assert dropdown.data.equals(sample_data)
#     except Exception as e:
#         pytest.fail(f"PlotDropDown init failed: {e}")

