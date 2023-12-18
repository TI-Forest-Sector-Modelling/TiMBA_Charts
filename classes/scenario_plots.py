import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from ipywidgets import interactive, widgets
from IPython.display import display, clear_output
import ipywidgets as widgets


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
        self.data = data
        self.reference_data_dropdown = self.choose_dropdown("Scenario")
        self.validation_data_dropdown = self.choose_dropdown("Scenario")
        self.comparator_dropdown = self.choose_dropdown("Comparator")
        self.regioncode_dropdown = self.choose_dropdown("RegionCode")
        self.domain_dropdown = self.choose_dropdown("domain")
        self.commodity_code_dropdown = self.choose_dropdown("CommodityCode")

        self.interactive_plot_update = interactive(self.update_heatmap_data,
                                                   reference_data = self.reference_data_dropdown,
                                                   validation_data = self.validation_data_dropdown,
                                                   comparator = self.comparator_dropdown,
                                                   region = self.regioncode_dropdown,
                                                   domain= self.domain_dropdown,
                                                   commodity = self.commodity_code_dropdown)     
        display(self.interactive_plot_update)


    def choose_dropdown(self, column):
        if (column == "Scenario"):
            options = list(self.data[column].unique())
            value = options[0]
        elif (column == "Comparator"):
            options = ['abs_quantity_diff', 'rel_quantity_diff', 'abs_price_diff', 'rel_price_diff']
            value = 'rel_quantity_diff'
        else:
            options = ['All'] + list(self.data[column].unique())
            value = 'All'

        return widgets.Dropdown(
            options=options,
            value=value,
            description=f'Select {column}:',
            disabled=False
        )    
    def update_heatmap_data(self, reference_data, validation_data, comparator, region, domain, commodity):
        region_filter = [region] if region != 'All' else self.data['RegionCode'].unique()
        domain_filter = [domain] if domain != 'All' else self.data['domain'].unique()
        commodity_filter = [commodity] if commodity != 'All' else self.data['CommodityCode'].unique()
        reference_filter = reference_data
        validation_filter = validation_data
        comparator_filter = comparator

        max_period = max(set(self.data[(self.data['Model'] == 'GFPMpt') &
                                       (self.data['Scenario'] == validation_filter)]['Period']))

        reference_data_filtered = self.data[self.data['Scenario'] == reference_filter]
        validation_data_filtered = self.data[self.data['Scenario'] == validation_filter]

        # Filter domain and commodities of interest
        reference_data_filtered = reference_data_filtered[(reference_data_filtered['domain'].isin(domain_filter)) &
                                                          (reference_data_filtered['RegionCode'].isin(region_filter)) &
                                                          (reference_data_filtered['CommodityCode'].isin(commodity_filter)) &
                                                          (reference_data_filtered['Period'] <= max_period)].reset_index(drop=True)
        
        reference_data_grouped = reference_data_filtered.groupby(['Period', 'CommodityCode']).sum().reset_index() 
        
        validation_data_filtered = validation_data_filtered[(validation_data_filtered['domain'].isin(domain_filter)) &
                                                            (validation_data_filtered['RegionCode'].isin(region_filter)) &
                                                            (validation_data_filtered['CommodityCode'].isin(commodity_filter))].reset_index(drop=True)
        
        validation_data_grouped = validation_data_filtered.groupby(['Period', 'CommodityCode']).sum().reset_index() 

        data_info = validation_data_grouped[['CommodityCode', 'Period']]

        abs_price_diff = pd.DataFrame(validation_data_grouped['price'] - reference_data_grouped['price']).rename(columns={'price': 'abs_price_diff'})
        abs_quantity_diff = pd.DataFrame(validation_data_grouped['quantity'] - reference_data_grouped['quantity']).rename(columns={'quantity': 'abs_quantity_diff'})
        rel_price_diff = pd.DataFrame((abs_price_diff['abs_price_diff'] / reference_data_grouped['price']) * 100).rename(columns={0: 'rel_price_diff'})
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
        plt.title(f'{comparator_filter} for {domain_filter}-quantities in {region_filter}')
        sns.heatmap(fig, annot=True, linewidths=.5, ax=ax, cbar_kws={'label': 'Deviation of GFPMpt from GFPM'})
        
class InteractivePrice:
    def __init__(self, data):
        self.data = data
        self.region_dropdown = self.create_dropdown('RegionCode', 'Select RegionCode:')
        self.model_dropdown = self.create_dropdown('Model', 'Select Model:')
        self.id_dropdown = self.create_dropdown('ID', 'Select ID:')
        self.domain_dropdown = self.create_dropdown('domain', 'Select Domain:')
        self.commodity_code_dropdown = self.create_dropdown('CommodityCode', 'Select CommodityCode:')

        self.interactive_plot_update = widgets.interactive(
            self.update_plot_data,
            region_code=self.region_dropdown,
            model=self.model_dropdown,
            id_value=self.id_dropdown,
            domain=self.domain_dropdown,
            commodity_code=self.commodity_code_dropdown
        )

        self.region_dropdown.observe(self.update_outputs, 'value')
        self.model_dropdown.observe(self.update_outputs, 'value')
        self.id_dropdown.observe(self.update_outputs, 'value')
        self.domain_dropdown.observe(self.update_outputs, 'value')
        self.commodity_code_dropdown.observe(self.update_outputs, 'value')

        self.output_plot = widgets.Output()
        self.output_table = widgets.Output()

        display(self.region_dropdown, self.model_dropdown, self.id_dropdown, self.domain_dropdown, self.commodity_code_dropdown)
        display(self.output_plot)
        display(self.output_table)

    def create_dropdown(self, column, description):
        dropdown = widgets.Dropdown(
            options=['Alle'] + list(self.data[column].unique()),
            value='Alle',
            description=description,
            disabled=False,
        )
        return dropdown

    def update_plot_data(self, region_code, model, id_value, domain, commodity_code):
        region_code_filter = [region_code] if region_code != 'Alle' else self.data['RegionCode'].unique()
        model_filter = [model] if model != 'Alle' else self.data['Model'].unique()
        id_filter = [id_value] if id_value != 'Alle' else self.data['ID'].unique()
        domain_filter = [domain] if domain != 'Alle' else self.data['domain'].unique()
        commodity_code_filter = [commodity_code] if commodity_code != 'Alle' else self.data['CommodityCode'].unique()

        filtered_data = self.data[
            (self.data['RegionCode'].isin(region_code_filter)) &
            (self.data['Model'].isin(model_filter)) &
            (self.data['ID'].isin(id_filter)) &
            (self.data['domain'].isin(domain_filter)) &
            (self.data['CommodityCode'].isin(commodity_code_filter))
        ]

        grouped_data = filtered_data.groupby(['Period', 'Scenario']).sum().reset_index()

        with self.output_plot:
            clear_output(wait=True)
            plt.figure(figsize=(12, 8))
            bar_width = 0.2
            for i, scenario_value in enumerate(grouped_data['Scenario'].unique()):
                subset = grouped_data[grouped_data['Scenario'] == scenario_value]
                x_positions = subset['Period'] + i * bar_width
                plt.bar(x_positions, subset['price'], width=bar_width, label=f'Scenario {scenario_value}')

            plt.title(f'Price for each scenario grouped by Period - RegionCode: {region_code}, Model: {model}, ID: {id_value}, Domain: {domain}, CommodityCode: {commodity_code}')
            plt.xlabel('Period')
            plt.ylabel('Price')
            plt.legend()
            plt.grid(True)
            plt.show()

        with self.output_table:
            clear_output(wait=True)
            display_table = filtered_data[['Period', 'RegionCode', 'Model', 'ID', 'domain', 'CommodityCode', 
                                           'Scenario', 'quantity', 'price']]
            display(display_table)

    def update_outputs(self, *args):
        self.update_plot_data(self.region_dropdown.value, self.model_dropdown.value, self.id_dropdown.value, 
                              self.domain_dropdown.value, self.commodity_code_dropdown.value)
