import pytest
import pandas as pd
from Toolbox.classes.ProcessManager import DataProcessor
import Toolbox.parameters.default_parameters as dp

@pytest.fixture
def dummy_data():
    overview_df = pd.DataFrame({
        "Model": ["M1", "M1"],
        "Scenario": ["S1", "S2"],
        "RegionCode": ["R1", "R2"],
        "CommodityCode": ["C1", "C2"],
        "domain": ["ManufactureCost", "TransportationExport"],
        "price": [10, 20],
        "quantity": [2, 3],
        "Period": [1, 2],
        "year": [2020, 2021]
    })
    forest_df = pd.DataFrame({
        "Scenario": ["S1", "S2"],
        "RegionCode": ["R1", "R2"],
        "Period": [1, 2],
        "ForStock": [100, 200],
        "ForArea": [10, 20],
        "supply_from_forest": [5, 10]
    })
    data_hist = pd.DataFrame({
        "Model": ["M1"],
        "Scenario": ["S0"],
        "RegionCode": ["R1"],
        "CommodityCode": ["C1"],
        "domain": ["ManufactureCost"],
        "price": [5],
        "quantity": [1],
        "Period": [0],
        "year": [2019]
    })
    country_data = pd.DataFrame({
        "RegionCode": ["R1", "R2"],
        "Continent": ["Europe", "Asia"],
        "Country": ["Country1", "Country2"],
        "ISO3": ["C1", "C2"]
    })
    commodity_data = pd.DataFrame({
        "CommodityCode": ["C1", "C2"],
        "Commodity": ["Com1", "Com2"],
        "Commodity_Group": ["G1", "G2"],
        "Unit": ["t", "t"]
    })
    return {
        dp.overview_db: overview_df,
        dp.forest_db: forest_df
    }, country_data, commodity_data, data_hist

@pytest.fixture
def processor(dummy_data):
    data, country_data, commodity_data, data_hist = dummy_data
    return DataProcessor(data, country_data, commodity_data, data_hist)

def test_combined_data(processor):
    combined = processor.combined_data()
    assert dp.overview_db in combined
    assert dp.forest_db in combined
    df = combined[dp.overview_db]
    assert all(df["Value"] == df["price"] * df["quantity"])
    assert "Manufacturing" in df["domain"].values
    assert "Export" in df["domain"].values
    forest_df = combined[dp.forest_db]
    assert "ISO3" in forest_df.columns
    assert "Continent" in forest_df.columns
    assert "year" in forest_df.columns

def test_pivot_map_data(processor):
    processor.combined_data()
    pivot_df = processor.pivot_map_data()
    required_cols = ["Continent","ISO3","domain","year","Commodity","Commodity_Group","S1","S2","S0"]
    for col in required_cols:
        assert col in pivot_df.columns
    assert pivot_df["S1"].sum() > 0

def test_pivot_map_forest_data(processor):
    processor.combined_data()
    stock_df, area_df = processor.pivot_map_forest_data()
    assert "Historic Data" in stock_df.columns
    assert "Historic Data" in area_df.columns
    assert stock_df["S1"].sum() > 0
    assert area_df["S1"].sum() > 0