OVERVIEW_DB_FILTERS = {
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
    "scenario": {
        "column": "Scenario",
        "placeholder": "Select Scenario..."
    }
}

WORLD_MAP_DB_FILTERS = {
    "continent": {
        "column": "Continent",
        "placeholder": "Select Continent..."
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
    "year": {
        "column": "year",
        "placeholder": "Select Year..."
    },
}

FOREST_DB_FILTERS = {
    "continent": {
        "column": "Continent",
        "placeholder": "Select Continent..."
    },
    "region": {
        "column": "ISO3",
        "placeholder": "Select Country..."
    },
    "scenario": {
        "column": "Scenario",
        "placeholder": "Select Scenario..."
    }
}

PRICE_DB_FILTERS = OVERVIEW_DB_FILTERS.copy()

TRADE_DB_FILTERS = {
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
    "scenario": {
        "column": "Scenario",
        "placeholder": "Select Scenario..."
    }
}

PLOT_FILTERS = {
    "trade": [
        "region",
        "continent",
        "commodity",
        "commodity_group",
        "scenario",
    ],
    "main": [
        "region",
        "continent",
        "commodity",
        "commodity_group",
        "scenario",
        "domain",
    ],
    "map": [
        "region",
        "continent",
        "commodity",
        "commodity_group",
        "domain",
    ],
    "forest": [
        "region",
        "continent",
        "scenario",
    ],
    "worldmap": [
        "continent",
        "commodity",
        "commodity_group",
        "year",
    ],
    "worldmap_forest": [
        "continent",
        "year",
    ],
}
