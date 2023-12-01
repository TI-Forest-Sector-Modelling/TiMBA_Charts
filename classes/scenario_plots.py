import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from ipywidgets import interactive, widgets
from IPython.display import display, clear_output

class sc_plot():
    def init(self):
        pass

    def predefined_plot(self, data: pd.DataFrame):
        data[['RegionCode', 'domain']] = data[['RegionCode', 'domain']].astype('str') # must be changed to perform groupby()
        grouped_data = data.groupby(['Period', 'Scenario']).sum().reset_index()
        plt.figure(figsize=(12, 8))

        for price_value in grouped_data['Scenario'].unique():
            subset = grouped_data[grouped_data['Scenario'] == price_value]
            plt.plot(subset['Period'], subset['quantity'], label=f'Scenario {price_value}')

        plt.title('Quantity for each country grouped by Period')
        plt.xlabel('period')
        plt.ylabel('Quantity')
        plt.legend()
        plt.grid(True)
        plt.show()
    
class PlotDropDown:
    def __init__(self,data): 
        self.data =data
        self.regioncode_dropdown = self.choose_dropdown("RegionCode")
        self.model_dropdown = self.choose_dropdown("Model")
        self.id_dropdown = self.choose_dropdown("ID")
        self.domain_dropdown = self.choose_dropdown("domain")
        self.commodity_code_dropdown = self.choose_dropdown("CommodityCode")

        self.interactive_heatmap = interactive(self.update_heatmap_data,
                                                   region = self.regioncode_dropdown,
                                                   model = self.model_dropdown,
                                                   id = self.id_dropdown,
                                                   domain= self.domain_dropdown,
                                                   commodity = self.commodity_code_dropdown)     
        display(self.interactive_heatmap)


    def choose_dropdown(self, column):
        options = ['Alle'] + list(self.data[column].unique())
        return widgets.Dropdown(
            options=options,
            value='Alle',
            description=f'Select {column}:',
            disabled=False
        )

    def update_heatmap_data(self, region, model, id, domain, commodity):
        region_filter = [region] if region != 'Alle' else self.data['RegionCode'].unique()
        model_filter = [model] if model != 'Alle' else self.data['Model'].unique()
        id_filter = [id] if id != 'Alle' else self.data['ID'].unique()
        domain_filter = [domain] if domain != 'Alle' else self.data['domain'].unique()
        commodity_filter = [commodity] if commodity != 'Alle' else self.data['CommodityCode'].unique()


        filtered_data = self.data[
            (self.data['RegionCode'].isin(region_filter)) &
            (self.data['Model'].isin(model_filter)) &
            (self.data['ID'].isin(id_filter)) &
            (self.data['domain'].isin(domain_filter)) &
            (self.data['CommodityCode'].isin(commodity_filter))
        ]
    
        grouped_data = filtered_data.groupby(['Period', 'Scenario']).sum().reset_index()

        plt.figure(figsize=(12, 8))

        for price_value in grouped_data['Scenario'].unique():
            subset = grouped_data[grouped_data['Scenario'] == price_value]
            plt.plot(subset['Period'], subset['quantity'], label=f'M: {price_value}')

        plt.title(f'quantity for each Period - RegionCode: {region}, Model: {model}, ID: {id}, Domain: {domain}, CommodityCode: {commodity}')
        plt.xlabel('period')
        plt.ylabel('quantity')
        plt.legend()
        plt.grid(True)
        plt.show()

class HeatmapDropDown:
    def __init__(self, data): 
        self.data_full = data["data_periods"]
        self.data_aggregated = data["data_aggregated"]
        self.selected_data_dropdown = self.choose_dropdown("SelectedData")
        self.reference_data_dropdown = self.choose_dropdown("Scenario")
        self.validation_data_dropdown = self.choose_dropdown("Scenario")
        self.comparator_dropdown = self.choose_dropdown("Comparator")
        self.spatialagg_dropdown = self.choose_dropdown("SpatialAggregation")
        self.domain_dropdown = self.choose_dropdown("domain")
        self.commodity_code_dropdown = self.choose_dropdown("CommodityCode")

        self.interactive_heatmap_update = interactive(self.update_heatmap_data,
                                                      selected_data = self.selected_data_dropdown,
                                                      reference_data = self.reference_data_dropdown,
                                                      validation_data = self.validation_data_dropdown,
                                                      comparator = self.comparator_dropdown,
                                                      spatial_aggregation = self.spatialagg_dropdown,
                                                      domain= self.domain_dropdown,
                                                      commodity = self.commodity_code_dropdown)     
        display(self.interactive_heatmap_update)


    def choose_dropdown(self, column):
        if (column == "SelectedData"):
            options = ["Regions", "Continents"]
            value = options[1]
        elif (column == "Scenario"):
            options = list(self.data_full[column].unique())
            value = options[0]
        elif (column == "Comparator"):
            options = ['abs_quantity_diff', 'rel_quantity_diff', 'abs_price_diff', 'rel_price_diff']
            value = 'rel_quantity_diff'

        elif (column == "SpatialAggregation"):
            if self.selected_data_dropdown.value == "Regions":
                options = ['All'] + list(self.data_full["RegionCode"].unique())
                value = 'All'
            elif self.selected_data_dropdown.value == "Continents":
                options = ['All'] + list(self.data_aggregated["ContinentNew"].unique())
                value = 'All'
        else:
            options = ['All'] + list(self.data_full[column].unique())
            value = 'All'

        return widgets.Dropdown(
            options=options,
            value=value,
            description=f'Select {column}:',
            disabled=False
        )    
    def update_heatmap_data(self, selected_data, reference_data, validation_data, comparator, spatial_aggregation, domain, commodity):

        if selected_data == "Regions":
            data = self.data_full
            column_filter = "RegionCode"
            price_column_filter = "price"
            aoi_filter = [spatial_aggregation] if spatial_aggregation != 'All' else self.data_full[column_filter].unique()
            
        elif selected_data == "Continents":
            data = self.data_aggregated
            column_filter = "ContinentNew"
            price_column_filter = "weighted_price"
            aoi_filter = [spatial_aggregation] if spatial_aggregation != 'All' else self.data_aggregated[column_filter].unique()


        domain_filter = [domain] if domain != 'All' else data['domain'].unique()
        commodity_filter = [commodity] if commodity != 'All' else data['CommodityCode'].unique()
        reference_filter = reference_data
        validation_filter = validation_data
        comparator_filter = comparator

        max_period = max(set(data[(data['Model'] == 'GFPMpt') &
                                  (data['Scenario'] == validation_filter)]['Period']))

        reference_data_filtered = data[data['Scenario'] == reference_filter]
        validation_data_filtered = data[data['Scenario'] == validation_filter]

        # Filter domain and commodities of interest
        reference_data_filtered = reference_data_filtered[(reference_data_filtered['domain'].isin(domain_filter)) &
                                                          (reference_data_filtered[column_filter].isin(aoi_filter)) &
                                                          (reference_data_filtered['CommodityCode'].isin(commodity_filter)) &
                                                          (reference_data_filtered['Period'] <= max_period)].reset_index(drop=True)
        
        reference_data_grouped = reference_data_filtered.groupby(['Period', 'CommodityCode']).sum().reset_index() 
        
        validation_data_filtered = validation_data_filtered[(validation_data_filtered['domain'].isin(domain_filter)) &
                                                            (validation_data_filtered[column_filter].isin(aoi_filter)) &
                                                            (validation_data_filtered['CommodityCode'].isin(commodity_filter))].reset_index(drop=True)
        
        validation_data_grouped = validation_data_filtered.groupby(['Period', 'CommodityCode']).sum().reset_index() 

        data_info = validation_data_grouped[['CommodityCode', 'Period']]

        abs_price_diff = pd.DataFrame(validation_data_grouped[price_column_filter] - reference_data_grouped[price_column_filter]).rename(columns={f'{price_column_filter}': 'abs_price_diff'})
        abs_quantity_diff = pd.DataFrame(validation_data_grouped['quantity'] - reference_data_grouped['quantity']).rename(columns={'quantity': 'abs_quantity_diff'})
        rel_price_diff = pd.DataFrame((abs_price_diff['abs_price_diff'] / reference_data_grouped[price_column_filter]) * 100).rename(columns={0: 'rel_price_diff'})
        rel_quantity_diff = pd.DataFrame((abs_quantity_diff['abs_quantity_diff'] / reference_data_grouped['quantity']) * 100).rename(columns={0: 'rel_quantity_diff'})

        data_heatmap = pd.concat([data_info,
                                  abs_price_diff['abs_price_diff'],
                                  abs_quantity_diff['abs_quantity_diff'],
                                  rel_price_diff['rel_price_diff'],
                                  rel_quantity_diff['rel_quantity_diff']], axis=1)

        data_heatmap.fillna(0, inplace=True)
        data_heatmap.replace(np.inf, 0, inplace=True)

        fig = data_heatmap.pivot('CommodityCode', 'Period', f'{comparator_filter}')  # TODO dynamize f'{rel_quantity_diff}' with drop down options
        f, ax = plt.subplots(figsize=(13, 9))
        plt.title(f'{comparator_filter} for {domain_filter}-quantities in {aoi_filter}')
        sns.heatmap(fig, annot=True, linewidths=.5, ax=ax, cbar_kws={'label': 'Deviation of GFPMpt from GFPM'})
        