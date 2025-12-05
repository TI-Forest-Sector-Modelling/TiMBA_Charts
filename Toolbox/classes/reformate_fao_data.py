import pandas as pd

fao = pd.read_csv('Forestry_subsetted_Data_reformatted.csv')

h_commodity = pd.read_csv('../Input/Additional_Information/commodity_info.csv', encoding="ISO-8859-1")
h_commodity = h_commodity[['GFPM_Code','FAO-Code']]
h_commodity.columns = ['GFPM_Code_Commodity','FAO_Code_commodity']

h_country = pd.read_csv('../Input/Additional_Information/country_info.csv', encoding="ISO-8859-1")
h_country = h_country[['Country-Code', 'FAOCou-Code']]
h_country.columns = ['GFPM_Code_Country','FAO_Code_Country']

fao_commodity = fao.merge(right=h_commodity, how='left',left_on='Item_Codes',right_on='FAO_Code_commodity').dropna()
fao_final = fao_commodity.merge(right=h_country, how='left',left_on='Area_Codes',right_on='FAO_Code_Country').dropna()
fao_final = fao_final.reset_index(drop=True)

fao_final_o5 = fao_final[fao_final.GFPM_Code_Country == 'o5']
print(fao_final_o5)

fao_final.to_csv('FAO_Data_py.csv')