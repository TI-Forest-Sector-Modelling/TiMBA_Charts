# import pandas as pd
# import pytest
# from Toolbox.classes.model_analysis import validation

# @pytest.fixture
# def validator():
#     return validation()

# @pytest.fixture
# def mock_data():
#     return pd.DataFrame({
#         'ID': [0, 1, 1],
#         'Scenario': ['Base', 'S1', 'S1'],
#         'RegionCode': ['A', 'A', 'A'],
#         'Continent': ['Europe', 'Europe', 'Europe'],
#         'domain': ['Supply', 'Supply', 'Supply'],
#         'CommodityCode': [101, 101, 101],
#         'year': [2020, 2020, 2020],
#         'quantity': [100, 80, 90]
#     })

# @pytest.mark.skip(reason="Fehler im test")
# def test_model_difference(validator, mock_data):
#     result = validator.model_difference(mock_data)
#     assert 'S1' in result.columns
#     assert isinstance(result, pd.DataFrame)
#     assert result['S1'].iloc[0] == 10

# def test_model_corrcoef(validator, mock_data):
#     result = validator.model_corrcoef(mock_data)
#     assert isinstance(result, pd.DataFrame)
#     assert not result.empty

# @pytest.mark.skip(reason="Fehler im test")
# def test_validation_std(validator, mock_data):
#     result = validator.validation(mock_data)
#     assert isinstance(result, pd.DataFrame)
#     assert result.columns[3] in ['S1']

# def test_reformate_external_data(validator):
#     sample_data = pd.DataFrame({
#         'Model': ['M1', 'M1'],
#         'Estimate': ['RoundwoodHarvest', 'ForestArea'],
#         'SSP': ['SSP1', 'SSP1'],
#         'Region': ['Europe', 'Europe'],
#         'RCP-SSP': ['Baseline_SSP1', 'Baseline_SSP1'],
#         2015: [1, 2],
#         2020: [3, 4],
#         2025: [5, 6],
#         2030: [7, 8],
#         2035: [9, 10]
#     })

#     result = validator.reformate_external_data(sample_data)
#     assert isinstance(result, pd.DataFrame)
#     assert set(result.columns) == {'Model', 'Parameter', 'Scenario', 'Region', 'Period', 'Data'}
#     assert result['Period'].max() <= 2035

# def test_add_world(validator):
#     df = pd.DataFrame({
#         'Model': ['GFPM']*2,
#         'Parameter': ['RoundwoodHarvest', 'RoundwoodHarvest'],
#         'Scenario': ['S1', 'S1'],
#         'Region': ['Europe', 'Asia'],
#         'Period': [2025, 2025],
#         'Data': [1000, 2000]
#     })
#     result = validator.add_world(df)
#     assert 'World' in result['Region'].values

# def test_convert_unit(validator):
#     df = pd.DataFrame({
#         'Parameter': ['RoundwoodHarvest', 'ForestArea', 'CarbonStockBiomass [MtCO2]'],
#         'Data': [1000, 2000, 44]
#     })
#     result = validator.convert_unit(df.copy())
#     assert result.loc[0, 'Data'] == 1
#     assert result.loc[1, 'Data'] == 2
#     assert round(result.loc[2, 'Data'], 2) == 12.0

# @pytest.mark.skip(reason="Fehler im test")
# def test_rename_parameter(validator):
#     df = pd.DataFrame({
#         'Parameter': ['CarbonStockBiomass [MtCO2]'],
#         'Scenario': ['model_rcp_ssp_otherinfo_SSP1']
#     })
#     result = validator.rename_parameter(df.copy())
#     assert result['Parameter'].iloc[0] == 'Total Forest Non-soil C Stock (MtC)'
#     assert result['Scenario'].iloc[0] == 'SSP1'

# def test_merge_data(validator):
#     df1 = pd.DataFrame({'Parameter': ['A'], 'Data': [1]})
#     df2 = pd.DataFrame({'Parameter': ['B'], 'Data': [2]})
#     result = validator.merge_data(df1, df2)
#     assert len(result) == 2
