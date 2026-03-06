import pytest
from pathlib import Path
import pandas as pd
from unittest.mock import patch, MagicMock
from Toolbox.classes.InputManager import import_pkl_data, import_formip_data, download_input_data
from Toolbox.parameters import default_parameters as dp
import Toolbox.parameters.paths as toolbox_paths

# load test data files in test_data folder
SCENARIO_PATH = Path("tests/test_data/scenarios")
ADDINFO_PATH = Path("tests/test_data/addinfo")

@pytest.fixture
def pkl_importer():
    return import_pkl_data(
        num_files_to_read=2,
        SCENARIOPATH=SCENARIO_PATH,
        ADDINFOPATH=ADDINFO_PATH
    )

@pytest.fixture
def formip_importer():
    return import_formip_data(
        ADDINFOPATH=ADDINFO_PATH,
        timba_data=pd.DataFrame(),
        only_baseline_sc=True
    )

# test for data import
def test_read_country_data(pkl_importer):
    country_data = pkl_importer.read_country_data()
    assert isinstance(country_data, pd.DataFrame)
    assert all(col in country_data.columns for col in ["RegionCode","Continent","Country","ISO3"])

def test_read_commodity_data(pkl_importer):
    commodity_data = pkl_importer.read_commodity_data()
    assert isinstance(commodity_data, pd.DataFrame)
    assert all(col in commodity_data.columns for col in ["Commodity","CommodityCode","Commodity_Group","Unit"])

def test_downcasting(pkl_importer):
    df = pd.DataFrame({
        "RegionCode": ["R1"], "CommodityCode": ["C1"], "domain": ["Supply"],
        "price": [1.23], "quantity": [10.0], "Period": [2020], "year": [2020],
        "Scenario": ["S1"], "Model": ["M1"]
    })
    df_casted = pkl_importer.downcasting(df)
    assert df_casted.price.dtype.name == "float32"
    assert df_casted.quantity.dtype.name == "float32"
    assert df_casted.RegionCode.dtype.name == "category"

# test for formip data
def test_process_formip_data(formip_importer):
    processed = formip_importer.process_formip_data()
    assert isinstance(processed, pd.DataFrame)
    assert "Year" in processed.columns
    assert "Data" in processed.columns