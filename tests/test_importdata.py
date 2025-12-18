import pytest
import pandas as pd
from unittest.mock import patch, mock_open
import pickle
import gzip
from pathlib import Path
from io import BytesIO
from Toolbox.classes.import_data import import_pkl_data 
import Toolbox.parameters.paths as toolbox_paths
import Toolbox.parameters.default_parameters as toolbox_parameters

@pytest.fixture
def import_pkl_instance():
    return import_pkl_data(SCENARIOPATH=toolbox_paths.SCINPUTPATH,
                           ADDINFOPATH=toolbox_paths.AIINPUTPATH,
                           num_files_to_read=1)

def create_mock_pkl_file(data):
    mock_pkl = pickle.dumps(data)
    mock_file = BytesIO(mock_pkl)
    return mock_file

def create_mock_gzip_file(data):
    mock_pkl = pickle.dumps(data)
    mock_gzip = BytesIO()
    with gzip.GzipFile(fileobj=mock_gzip, mode='wb') as f:
        f.write(mock_pkl)
    mock_gzip.seek(0)
    return mock_gzip

def test_open_pickle_success(import_pkl_instance):
    mock_data = {'test': 'data'}
    mock_file = create_mock_pkl_file(mock_data)
    
    with patch("builtins.open", return_value=mock_file):
        result = import_pkl_instance.open_pickle("dummy_path.pkl")
    assert result == mock_data

@patch('pandas.read_csv')
def test_read_country_data(mock_read_csv, import_pkl_instance):
    mock_data = pd.DataFrame({
        "Country-Code": [1, 2],
        "ContinentNew": ["A", "B"],
        "Country": ["X", "Y"],
        "ISO-Code": ["x1", "y1"]
    })
    mock_read_csv.return_value = mock_data

    result = import_pkl_instance.read_country_data()
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["RegionCode", "Continent", "Country", "ISO3"]
    assert result["Country"].dtype == "category"
    mock_read_csv.assert_called_once()

@patch('pandas.read_csv')
def test_read_commodity_data(mock_read_csv, import_pkl_instance):
    mock_data = pd.DataFrame({
        "Commodity": ["A", "B"],
        "CommodityCode": ["C1", "C2"],
        "Commodity_Group": ["G1", "G2"]
    })
    mock_read_csv.return_value = mock_data
    result = import_pkl_instance.read_commodity_data()
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["Commodity", "CommodityCode", "Commodity_Group"]
    assert result["Commodity"].dtype == "category"
    mock_read_csv.assert_called_once()

@patch('pandas.read_csv')
def test_read_historic_data(mock_read_csv, import_pkl_instance):
    mock_data = pd.DataFrame({
        "RegionCode": [1, 2],
        "CommodityCode": [3, 4],
        "domain": ["A", "B"],
        "price": [1.0, 2.0],
        "quantity": [3.0, 4.0],
        "Period": [5, 6],
        "year": [2020, 2021],
        "Scenario": ["S1", "S2"],
        "Model": ["M1", "M2"]
    })
    mock_read_csv.return_value = mock_data
    result = import_pkl_instance.read_historic_data()
    assert isinstance(result, pd.DataFrame)
    assert result["RegionCode"].dtype == "category"
    assert result["price"].dtype == "float32"
    mock_read_csv.assert_called_once()

def test_downcasting(import_pkl_instance):
    data = pd.DataFrame({
        "RegionCode": [1, 2],
        "CommodityCode": [3, 4],
        "domain": ["A", "B"],
        "price": [1.0, 2.0],
        "quantity": [3.0, 4.0],
        "Period": [5, 6],
        "year": [2020, 2021],
        "Scenario": ["S1", "S2"],
        "Model": ["M1", "M2"]
    })

    result = import_pkl_instance.downcasting(data)

    assert result["RegionCode"].dtype == "category"
    assert result["price"].dtype == "float32"
    assert result["Period"].dtype == "int16"

def test_add_consumption(import_pkl_instance):
    data = pd.DataFrame({
        "quantity_ManufactureCost": [1, 2],
        "quantity_Supply": [3, 4],
        "quantity_TransportationExport": [1, 1],
        "quantity_TransportationImport": [1, 1],
        "price_ManufactureCost": [10, 20],
        "price_Supply": [30, 40],
        "price_TransportationExport": [10, 10],
        "price_TransportationImport": [10, 10],
    })

    result = import_pkl_instance.add_consumption(data.copy())

    assert "quantity" in result.columns
    assert "price" in result.columns
    assert result["domain"].iloc[0] == "Consumption"
    assert (result["quantity"] >= 0).all()

def test_add_net_exports(import_pkl_instance):
    data = pd.DataFrame({
        "quantity_TransportationExport": [2, 3],
        "quantity_TransportationImport": [1, 1],
        "price_TransportationExport": [20, 30]
    })
    result = import_pkl_instance.add_net_exports(data.copy())
    assert "quantity" in result.columns
    assert "price" in result.columns
    assert result["domain"].iloc[0] == "Net Exports"
    assert (result["quantity"] == [1, 2]).all()

def test_add_net_imports(import_pkl_instance):
    data = pd.DataFrame({
        "quantity_TransportationImport": [2, 3],
        "quantity_TransportationExport": [1, 1],
        "price_TransportationImport": [20, 30]
    })
    result = import_pkl_instance.add_net_imports(data.copy())
    assert "quantity" in result.columns
    assert "price" in result.columns
    assert result["domain"].iloc[0] == "Net Imports"
    assert (result["quantity"] == [1, 2]).all()

def test_add_production(import_pkl_instance):
    data = pd.DataFrame({
        "quantity_ManufactureCost": [1, 2],
        "quantity_Supply": [3, 4],
        "price_ManufactureCost": [10, 20],
        "price_Supply": [30, 40]
    })
    result = import_pkl_instance.add_production(data.copy())
    assert "quantity" in result.columns
    assert "price" in result.columns
    assert result["domain"].iloc[0] == "Production"
    assert (result["quantity"] == [4, 6]).all()

def test_concat_calc_domains(import_pkl_instance):
    origin_data = pd.DataFrame({
        'RegionCode': [1, 2],
        'CommodityCode': [3, 4],
        'Period': [5, 6],
        'year': [2020, 2021],
        'domain': ['A', 'B'],
        'price': [1.0, 2.0],
        'quantity': [3.0, 4.0],
        'other_col': [7, 8]
    })
    calc_data = pd.DataFrame({
        'RegionCode': [1, 2],
        'CommodityCode': [3, 4],
        'Period': [5, 6],
        'year': [2020, 2021],
        'domain': ['C', 'D'],
        'price': [5.0, 6.0],
        'quantity': [7.0, 8.0],
        'another_col': [9, 10]
    })
    result = import_pkl_instance.concat_calc_domains(origin_data, calc_data)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 4
    assert 'other_col' in result.columns
    assert 'another_col' not in result.columns

def test_add_calculated_domains(import_pkl_instance):
    data = {
        "data_periods": pd.DataFrame({
            'RegionCode': [1, 1, 2, 2],
            'CommodityCode': [101, 101, 102, 102],
            'Period': [1, 2, 1, 2],
            'year': [2020, 2021, 2020, 2021],
            'domain': ['A', 'B', 'A', 'B'],
            'price': [1.0, 2.0, 3.0, 4.0],
            'quantity': [10.0, 20.0, 30.0, 40.0]
        })
    }
    with patch.object(import_pkl_data, 'add_net_exports') as mock_add_net_exports, \
            patch.object(import_pkl_data, 'add_net_imports') as mock_add_net_imports:
        mock_add_net_exports.return_value = pd.DataFrame({
            'RegionCode': [1, 2],
            'CommodityCode': [101, 102],
            'Period': [1, 1],
            'year': [2020, 2020],
            'domain': ['Net Exports', 'Net Exports'],
            'price': [5.0, 6.0],
            'quantity': [50.0, 60.0]
        })
        mock_add_net_imports.return_value = pd.DataFrame({
            'RegionCode': [1, 2],
            'CommodityCode': [101, 102],
            'Period': [1, 1],
            'year': [2020, 2020],
            'domain': ['Net Imports', 'Net Imports'],
            'price': [7.0, 8.0],
            'quantity': [70.0, 80.0]
        })
        result = import_pkl_instance.add_calculated_domains(data)
        assert isinstance(result, pd.DataFrame)
        assert mock_add_net_exports.called
        assert mock_add_net_imports.called

def test_concat_scenarios(import_pkl_instance):
    data = {
        "data_periods": pd.DataFrame({
            'RegionCode': [1, 2],
            'CommodityCode': [3, 4],
            'Period': [5, 6],
            'year': [2020, 2021],
            'domain': ['A', 'B'],
            'price': [1.0, 2.0],
            'quantity': [3.0, 4.0]
        })
    }
    sc_name = "scenario1"
    data_prev = {
        "data_periods": pd.DataFrame({
            'RegionCode': [5, 6],
            'CommodityCode': [7, 8],
            'Period': [9, 10],
            'year': [2022, 2023],
            'domain': ['C', 'D'],
            'price': [5.0, 6.0],
            'quantity': [7.0, 8.0],
            'Scenario': ['scenario0', 'scenario0'],
            'Model': ['model0', 'model0']
        })
    }
    ID = 1
    with patch.object(import_pkl_data, 'add_calculated_domains') as mock_add_calculated_domains:
        mock_add_calculated_domains.return_value = data["data_periods"]
        import_pkl_instance.concat_scenarios(data, sc_name, data_prev, ID)
        assert "Scenario" in data["data_periods"].columns
        assert "Model" in data["data_periods"].columns

# def test_combined_data(import_pkl_instance, tmp_path):
#     test_data = {'data_periods': pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})}
#     file1 = tmp_path / "scenario1.pkl"
#     file2 = tmp_path / "scenario2.pkl"
#     with gzip.open(file1, 'wb') as f:
#         pickle.dump(test_data, f)
#     with gzip.open(file2, 'wb') as f:
#         pickle.dump(test_data, f)
#     with patch.object(import_pkl_data, 'read_historic_data') as mock_read_historic_data, \
#             patch.object(import_pkl_data, 'read_country_data') as mock_read_country_data, \
#             patch.object(import_pkl_data, 'read_commodity_data') as mock_read_commodity_data:
#         mock_read_historic_data.return_value = pd.DataFrame({'hist_col1': [5, 6], 'hist_col2': [7, 8]})
#         mock_read_country_data.return_value = pd.DataFrame({'RegionCode': [1, 2], 'Continent': ['A', 'B'], 'Country': ['X', 'Y'], 'ISO3': ['x1', 'y1']})
#         mock_read_commodity_data.return_value = pd.DataFrame({'Commodity': ['C1', 'C2'], 'CommodityCode': [101, 102], 'Commodity_Group': ['G1', 'G2']})
#         import_pkl_instance.SCENARIOPATH = tmp_path
#         import_pkl_instance.num_files_to_read = 2
#         result = import_pkl_instance.combined_data()
#         assert isinstance(result, dict)
#         assert 'data_periods' in result
#         assert mock_read_historic_data.called
#         assert mock_read_country_data.called
#         assert mock_read_commodity_data.called