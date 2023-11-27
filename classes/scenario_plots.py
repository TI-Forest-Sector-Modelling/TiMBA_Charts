import pandas as pd
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

        self.interactive_plot_update = interactive(self.update_plot_data,
                                                   region = self.regioncode_dropdown,
                                                   model = self.model_dropdown,
                                                   id = self.id_dropdown,
                                                   domain= self.domain_dropdown,
                                                   commodity = self.commodity_code_dropdown)     
        display(self.interactive_plot_update)


    def choose_dropdown(self, column):
        options = ['Alle'] + list(self.data[column].unique())
        return widgets.Dropdown(
            options=options,
            value='Alle',
            description=f'Select {column}:',
            disabled=False
        )

    def update_plot_data(self, region, model, id, domain, commodity):
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