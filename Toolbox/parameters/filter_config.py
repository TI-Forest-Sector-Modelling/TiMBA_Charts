OVERVIEW_DB_FILTERS = {
    "scenario": {
        "column": "Scenario",
        "placeholder": "Select Scenario..."
    },
    "continent": {
        "column": "Continent",
        "placeholder": "Select Continent..."
    },
    "region": {
        "column": "ISO3",
        "placeholder": "Select Country..."
    },
    "domain": {
        "column": "domain",
        "placeholder": "Select Domain..."
    },
    "commodity": {
        "column": "Commodity",
        "placeholder": "Select Commodity..."
    },
    "commodity_group": {
        "column": "Commodity_Group",
        "placeholder": "Select Commodity Group..."
    },
}

WORLD_MAP_DB_FILTERS = {
    "continent": {
        "column": "Continent",
        "placeholder": "Select Continent..."
    },
    "year": {
        "column": "year",
        "placeholder": "Select Year..."
    },
    "commodity": {
        "column": "Commodity",
        "placeholder": "Select Commodity..."
    },
    "commodity_group": {
        "column": "Commodity_Group",
        "placeholder": "Select Commodity Group..."
    },
    "refscenario": {
        "column": "Scenario",
        "placeholder": "Select Reference Scenario..."
    },
    "altscenario": {
        "column": "Scenario",
        "placeholder": "Select Alternative Scenario..."
    },
}

FOREST_DB_FILTERS = {
    "scenario": {
        "column": "Scenario",
        "placeholder": "Select Scenario..."
    },
    "continent": {
        "column": "Continent",
        "placeholder": "Select Continent..."
    },
    "region": {
        "column": "ISO3",
        "placeholder": "Select Country..."
    },
}

PRICE_DB_FILTERS = OVERVIEW_DB_FILTERS.copy()

TRADE_DB_FILTERS = {
    "scenario": {
        "column": "Scenario",
        "placeholder": "Select Scenario..."
    },
    "continent": {
        "column": "Continent",
        "placeholder": "Select Continent..."
    },
    "region": {
        "column": "ISO3",
        "placeholder": "Select Country..."
    },
    "commodity": {
        "column": "Commodity",
        "placeholder": "Select Commodity..."
    },
    "commodity_group": {
        "column": "Commodity_Group",
        "placeholder": "Select Commodity Group..."
    },
}

BILATERAL_TRADE_DB_FILTERS = {
    "exporter": {
        "column": "Exporter",
        "placeholder": "Select exporter country..."
    },
    "exporter_continent": {
        "column": "Continent_Exporter",
        "placeholder": "Select exporter continent..."
    },
    "importer": {
        "column": "Importer",
        "placeholder": "Select importer country..."
    },
    "importer_continent": {
        "column": "Continent_Importer",
        "placeholder": "Select importer continent..."
    },
    "commodity": {
        "column": "Commodity",
        "placeholder": "Select Commodity..."
    },
    "commodity_group": {
        "column": "Commodity_Group",
        "placeholder": "Select Commodity Group..."
    },
}

PLOT_FILTERS = {
    "bilateral_trade": [
        "exporter",
        "exporter_continent",
        "importer",
        "importer_continent",
        "commodity",
        "commodity_group"
    ],
    "trade": [
        "scenario",
        "continent",
        "region",
        "commodity",
        "commodity_group",
    ],
    "main": [
        "scenario",
        "continent",
        "region",
        "commodity",
        "commodity_group",
        "domain",
    ],
    "map": [
        "scenario",
        "continent",
        "region",
        "commodity",
        "commodity_group",
        "domain",
    ],
    "forest": [
        "scenario",
        "continent",
        "region",
    ],
    "worldmap": [
        "continent",
        "year",
        "commodity",
        "commodity_group",
    ],
    "worldmap_forest": [
        "continent",
        "year",
    ],
}
