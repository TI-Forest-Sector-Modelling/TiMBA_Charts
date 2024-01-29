forest_data = data['Forest']
country_data = import_pkl.read_country_data()
forest_data_world = import_pkl.read_forest_data_gfpm(country_data=country_data)
forest_data = forest_data[forest_data_world.columns]
forest_data = pd.concat([forest_data, forest_data_world], axis= 0)