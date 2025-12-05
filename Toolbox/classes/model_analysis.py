import pandas as pd
import numpy as np
import os
from pathlib import Path
from enum import Enum
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class parameters(Enum):
    pass

class validation():
    def init(self):
        pass

    def readin_country_data(self):
        path = os.path.dirname(Path(__file__).resolve().parents[0])
        country_data = pd.read_csv(f'{path}\\Input\\Additional_Information\\country_info.csv', encoding = "ISO-8859-1")
        return country_data
    
    def readin_external_data(self):
        path = os.path.dirname(Path(__file__).resolve().parents[0])
        external_data = pd.read_csv(f'{path}\\Input\\Additional_Information\\external_model_data.csv', encoding = "ISO-8859-1")
        return external_data

    def model_difference(self, data: pd.DataFrame):
        data_gfpm = data[data.ID==0].reset_index(drop=True)
        data_gfpm = data_gfpm[['RegionCode','domain',"CommodityCode","quantity"]]
        for i in data.ID.unique():
            sc_name = list(data.Scenario[data.ID==i])[0]
            data_gfpmpt = data[data.ID==i].reset_index(drop=True)
            data_gfpm[sc_name] = data_gfpm.quantity - data_gfpmpt.quantity
        return data_gfpm
    
    def model_corrcoef(self, data: pd.DataFrame, unit: str = 'quantity'):
        data_gfpm = data[data.ID==0].reset_index(drop=True)
        column_list = ['Continent','domain','CommodityCode','year']
        data_gfpm = data_gfpm[column_list + [unit]]
        cor_df = pd.DataFrame()
        for column in column_list:
            corr_full = pd.DataFrame()
            for i in data.ID.unique():
                sc_name = list(data.Scenario[data.ID==i])[0]
                data_gfpmpt = data[data.ID==i].reset_index(drop=True)
                data_gfpm[sc_name] = data_gfpmpt.quantity
                correlations = data_gfpm.groupby(column)[[unit,sc_name]].corr().iloc[0::2,-1].reset_index()
                corr_full = pd.concat([corr_full,correlations[sc_name]], axis=1)
            correlations.rename(columns={column: "ID"}, inplace=True)
            correlations = pd.concat([correlations["ID"], corr_full], axis=1)
            correlations["column"] = column
            cor_df = pd.concat([cor_df,correlations],axis=0)

        color_palette=['royalblue', 'peru', 'forestgreen', 
               'orangered', 'darkviolet', 'darkcyan', 
               'brown', 'pink', 'olive', 'grey']
        width = 0.5  # the width of the bars
        data_barplot = cor_df[cor_df.column == "domain"]
        
        num_sc = len(data_barplot.ID)
        name_df = pd.DataFrame()
        cor_df = data_barplot[data_barplot.columns[1:-2]]
        for i in range(0,num_sc):
            title_name = data_barplot[data_barplot.columns[0:1]].iloc[i:i+1]
            name_df = pd.concat([name_df,title_name])
        
        fig, axes =  plt.subplots(5, 1, sharex=False, sharey= False, figsize=(3,9)) 
        for i in range(0,num_sc):
            value = pd.DataFrame(cor_df.iloc[i])
            mean_val = value.mean()
            diff_val = value - mean_val
            ylim_max = diff_val.max().values * 1.05
            ylim_min = diff_val.min().values * 0.95
            diff_val.plot.bar(grid=True, color=color_palette[i], width=0.9, ax=axes[i])
            axes[i].title.set_text(str(name_df.iloc[i].values))
            axes[i].get_legend().remove()
            axes[i].set_ylim([ylim_min,ylim_max])
            if i < 4:
                axes[i].get_xaxis().set_visible(False)
        
        fig.tight_layout(pad=1.0)
        #plt.show()


            # courses = data_plot.columns
            # values = data_plot.iloc[i].values
            # fig = plt.figure(figsize = (10, 5))
            # values.plt.bar(courses,axs = axs[i])#, color='royalblue',
                          #color_paette, 
                          #width = width)
            # axs[i].plt.xticks(rotation=30, ha='right') 
            # axs[i].plt.ylim([min(values)*0.995, max(values)*1.005])   
            # axs[i].plt.xlabel("")
            # axs[i].plt.ylabel("")
            # axs[i].plt.title(title_name.values[0][0])
            # plt.show()
        return cor_df
    
    def validation(self, data: pd.DataFrame):
        data_vali = data[data.ID==0].reset_index(drop=True)
        data_std_prev = []
        for i in data.ID.unique():
            print(data.Scenario[data.ID == i][0])
            sc_name = data.Scenario[data.ID == i][0]
            data_gfpm = data_vali
            data_gfpmpt = data[data.ID==i].reset_index(drop=True)
            data_gfpm["vali"] = data_gfpm.quantity - data_gfpmpt.quantity
            data_std = pd.DataFrame(data_gfpm.groupby(['RegionCode','domain',"CommodityCode"])["vali"].std()).reset_index()
            data_std.columns = ["Region", "Domain","Commodity",sc_name]
            data_std_index = data_std[["Region", "Domain","Commodity"]]
            data_std_prev = pd.concat([pd.DataFrame(data_std_prev),pd.DataFrame(data_std[sc_name])], axis=1)
        data_std = pd.concat([data_std_index, data_std_prev], axis=1)
        fourth_quantile = data_std[data_std.columns[3]].quantile([.75])
        data_std = data_std.sort_values(by=data_std.columns[3], ascending=False)
        #data_std_count = pd.DataFrame(data_std.groupby(['Region','Domain']).count()).reset_index()
        return data_std
    
    def filter_data(self, data: pd.DataFrame, country_data: pd.DataFrame):
        
        data_filtered = pd.DataFrame()

        for data_key in data.keys():
            data_fin = pd.DataFrame() 
            #  filter carbon
            if data_key == 'Carbon':
                data_temp = data[data_key]
                data_info = data_temp[['RegionCode', 'Period', 'Scenario', 'Model']]

                col_list = ['CarbonStockBiomass [MtCO2]', 'CarbonStockHWP [MtCO2]']  
                for col in col_list:
                    data_reformated = pd.DataFrame()
                    data_col = data_temp[col]
                    data_reformated['Data'] = data_col
                    data_reformated['Parameter'] = col
                    data_reformated = pd.concat([data_info, data_reformated], axis=1)
                    data_fin = pd.concat([data_fin, data_reformated], axis=0).reset_index(drop=True)

            # filter weighted roundwood prices and roundwood harvest
            if data_key == 'Data':
                # compute weighted roundwood prices
                data_temp = data[data_key]
                data_temp = data_temp[[x in [78, 81] for x in data_temp['CommodityCode']]].reset_index(drop=True)
                data_temp = data_temp[data_temp['domain'] == 'Supply'].reset_index(drop=True)
                data_temp = data_temp[data_temp['Scenario'] != 'FAOStat']
                data_temp['value'] = data_temp['price'] * data_temp['quantity']
                data_price = (data_temp.groupby(['Period', 'Scenario', 'Model'])['value'].sum() /
                             data_temp.groupby(['Period', 'Scenario', 'Model'])['quantity'].sum()).reset_index()
                data_price = data_price.rename(columns={0: 'Data'})
                data_price['Region'] = 'World'
                data_price['Parameter'] = 'wtRoundwoodPrice'

                # compute roundwood harvest
                data_quantity = data_temp.groupby(['RegionCode', 'Period', 'Scenario', 'Model'])['quantity'].sum().reset_index()
                data_quantity = data_quantity.merge(country_data[['Country-Code', 'ContinentValidation']], left_on='RegionCode',
                                                    right_on='Country-Code', how='left')
                data_quantity = data_quantity.rename(columns={'quantity': 'Data'})
                data_quantity = data_quantity.groupby(['Model', 'Scenario', 'ContinentValidation', 'Period'])['Data'].sum().reset_index()
                data_quantity = data_quantity.rename(columns={'ContinentValidation': 'Region'})
                data_quantity['Parameter'] = 'RoundwoodHarvest'

                data_fin = pd.concat([data_price, data_quantity], axis=0).reset_index(drop=True)

            # filter forest
            if data_key == 'Forest':
                data_temp = data[data_key]
                data_temp = data_temp.drop_duplicates().reset_index(drop=True)
                data_temp['Parameter'] = 'ForestArea'
                data_temp = data_temp.rename(columns={'ForArea': 'Data'})

                data_fin = data_temp[['Model', 'Parameter', 'Scenario', 'RegionCode', 'Period', 'Data']]

            # Aggregation 
            if 'RegionCode' in data_fin.columns:
                data_fin = data_fin.merge(country_data[['Country-Code', 'ContinentValidation']], left_on='RegionCode',
                                           right_on='Country-Code', how='left')
                
                data_fin = data_fin.groupby(['Model', 'Parameter', 'Scenario', 'ContinentValidation', 'Period'])['Data'].sum().reset_index()
                data_fin = data_fin.rename(columns={'ContinentValidation': 'Region'})


            data_filtered = pd.concat([data_filtered, data_fin], axis=0)

        return data_filtered
    
    def reformate_external_data(self, data: pd.DataFrame):
        data = data[data['RCP-SSP'].str.contains('Baseline')].reset_index(drop=True)
        periods = data.columns[6:11]  # select data until 2055
        data_reformated = pd.DataFrame()
        for parameter in data['Estimate'].unique()[:-1]:
            data_temp = data[data['Estimate'] == parameter].reset_index(drop=True)
            data_info = data_temp.iloc[:, : 6]
            data_periods = pd.DataFrame()
            for period in periods:
                data_period = data_temp[period]
                data_period = pd.DataFrame(data_period).rename(columns={period: 'Data'})
                data_period['Period'] = int(period)
                data_period = pd.concat([data_info, data_period], axis=1)
                data_periods = pd.concat([data_periods, data_period], axis=0)

            data_reformated = pd.concat([data_reformated, data_periods], axis=0)
        data_reformated = data_reformated.rename(columns={'Estimate': 'Parameter',
                                                           'SSP': 'Scenario'})
        data_reformated = data_reformated[['Model', 'Parameter', 'Scenario', 'Region', 'Period', 'Data']]

        return data_reformated

    def period_structure(self, data: pd.DataFrame):
        data = data[data['Model'] == 'GFPMpt']
        period_data = data[['Period', 'year']].drop_duplicates().reset_index(drop=True)
        return period_data
    
    def align_period_data(self, data: pd.DataFrame, period_data: pd.DataFrame):
        data = data.merge(period_data, left_on='Period', right_on='Period', how='left')
        period_len = 10
        period_list = range(2015, 2055, period_len)
        data_aligned = pd.DataFrame()

        for period in period_list:
            """if period == 2015:  # Baseperiod
                data_period = data[data['year'] == period]
                data_period_index = data[data['year'] == period].index
                data_period.loc[data_period_index, 'Period'] = data_period.loc[data_period_index, 'year']
                data_period = data_period[['Model', 'Parameter', 'Scenario', 'Region', 'Period', 'Data']]"""

            if period == 2025:  # Mixed period with single- and multiple-year-period 
                data_single_year_period = data[[x in list(range(period - period_len, period))[1:] for x in data['year']]]
                data_multiple_year_period = data[data['year'] == period]

                data_single_year_period = data_single_year_period.groupby(['Model', 'Parameter', 'Scenario', 'Region'])['Data'].sum().reset_index()
                data_multiple_year_period = data_multiple_year_period.groupby(['Model', 'Parameter', 'Scenario', 'Region'])['Data'].sum().reset_index()
                data_multiple_year_period.loc[data_multiple_year_period.index,'Data'] = data_multiple_year_period.loc[data_multiple_year_period.index,'Data'] * 5
                
                data_single_year_period = data_single_year_period.reset_index(drop=True)
                data_multiple_year_period = data_multiple_year_period.reset_index(drop=True)
                
                data_single_year_period['Data'] = (data_single_year_period['Data'] + data_multiple_year_period['Data']) / 10
                data_single_year_period['Period'] = period
                data_period = data_single_year_period.reset_index(drop=True)                                             
            else:  # all other multiple-year-periods
                data_period = data[data['year'] == period]
                data_period_index = data[data['year'] == period].index
                data_period.loc[data_period_index, 'Period'] = data_period.loc[data_period_index, 'year']
                data_period = data_period[['Model', 'Parameter', 'Scenario', 'Region', 'Period', 'Data']].reset_index(drop=True)
                
            data_aligned = pd.concat([data_aligned, data_period], axis=0).reset_index(drop=True)

        return data_aligned
    
    def add_world(self, data: pd.DataFrame):

        data = data[data['Region'] != 'Rest of World'].reset_index(drop=True)
        data_new = pd.DataFrame()

        list_parameter = ['CarbonStockBiomass [MtCO2]', 'CarbonStockHWP [MtCO2]', 'ForestArea', 'RoundwoodHarvest']

        for parameter in data['Parameter'].unique():
            data_temp = data[data['Parameter'] == parameter]
            
            if parameter in list_parameter:
                data_world = data_temp.groupby(['Model', 'Parameter', 'Scenario', 'Period'])['Data'].sum().reset_index()
                data_world['Region'] = 'World'
                data_temp = pd.concat([data_temp, data_world], axis=0).reset_index(drop=True)
            data_new = pd.concat([data_new, data_temp], axis=0).reset_index(drop=True)
        
        return data_new


    
    def convert_unit(self, data: pd.DataFrame):

        # Convert harvest (tsd m³ to M m³):
        col_name = 'RoundwoodHarvest'
        selection_index = data[data['Parameter'] == col_name].index
        data.loc[selection_index, 'Data'] = data.loc[selection_index, 'Data'] / 1000

        # Convert forest area (tsd ha to M ha)
        col_name = 'ForestArea'
        selection_index = data[data['Parameter'] == col_name].index
        data.loc[selection_index, 'Data'] = data.loc[selection_index, 'Data'] / 1000

        # Convert carbon (CO2 to C):
        col_name = ['CarbonStockBiomass [MtCO2]', 'CarbonStockHWP [MtCO2]']
        selection_index = data[[x in col_name for x in data['Parameter']]].index
        data.loc[selection_index, 'Data'] = data.loc[selection_index, 'Data'] / (44/12)

        return data

    def rename_parameter(self, data: pd.DataFrame):
        # rename parameter
        parameter_name = {'CarbonStockBiomass [MtCO2]': 'Total Forest Non-soil C Stock (MtC)',
                          'ForestArea': 'Forest Area (Mha)',
                          'RoundwoodHarvest': 'Roundwood Harvest (Mm3/yr)',
                          'wtRoundwoodPrice': 'Wt Avg Roundwood Price (/m3)'}
        
        for parameter in parameter_name.keys():
            selection_index = data[data['Parameter'] == parameter].index
            data.loc[selection_index, 'Parameter'] = parameter_name[parameter]
        
        # rename scenario
        data['Scenario'] = data['Scenario'].str.split('_', expand=True)[5]

        return data

    def merge_data(self, data: pd.DataFrame, external_data: pd.DataFrame):
        data_fin = pd.concat([data, external_data], axis=0).reset_index(drop=True)
        
        return data_fin