import pytest
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from Toolbox.classes.LayoutManager import Layout, FilterLayout

# -----------------------
# Layout Tests
# -----------------------

def test_graph_card():
    graph = Layout._graph_card("test-graph")
    # Prüfen, ob es ein html.Div ist
    assert isinstance(graph, html.Div)
    # Prüfen, ob das Child ein dcc.Graph ist
    assert isinstance(graph.children, dcc.Graph)
    # Prüfen, ob die ID korrekt gesetzt ist
    assert graph.children.id == "test-graph"
    # Prüfen, ob style enthalten ist
    assert "height" in graph.children.style

def test_download_button():
    button_list = Layout.download_button("btn1")
    assert isinstance(button_list, list)
    btn_div = button_list[0]
    assert isinstance(btn_div, html.Div)
    btn = btn_div.children
    assert isinstance(btn, dbc.Button)
    assert btn.id == "btn1"
    assert btn.color == "primary"

def test_legend_card():
    colors = {"Scenario1": "red", "Scenario2": "blue"}
    scenarios = ["Scenario1", "Scenario2"]
    card = Layout._legend_card(colors, scenarios)
    assert isinstance(card, dbc.Card)
    # Prüfen, ob Children existieren
    assert len(card.children) == 1
    div = card.children[0]
    assert isinstance(div, html.Div)
    # Prüfen, ob die Anzahl der Items stimmt
    assert len(div.children) == 2  # zwei Szenarien

def test_legend_card_world_map():
    card = Layout._legend_card_world_map()
    assert isinstance(card, dbc.Card)
    assert len(card.children) == 1
    # Prüfen, ob die innere Struktur Div enthält
    inner_div = card.children[0]
    assert isinstance(inner_div, html.Div)

def test_ledgend_items():
    colors = {"S1": "red", "S2": "green"}
    scenarios = ["S1", "S2"]
    items = Layout.ledgend_items(colors, scenarios)
    assert isinstance(items, list)
    for i, s in enumerate(scenarios):
        div = items[i]
        assert isinstance(div, html.Div)
        span = div.children[1]
        assert span.children == s
        # Prüfen, ob Farbe korrekt gesetzt ist
        color_div = div.children[0]
        assert color_div.style["backgroundColor"] == colors[s]

# -----------------------
# FilterLayout Tests
# -----------------------

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Region": ["A", "B", "C"],
        "Country": ["X", "Y", "Z"],
        "Category": ["Cat1", "Cat2", "Cat1"],
        "Value": [1, 2, 3],
        "Extra1": [0,0,0],
        "Extra2": [0,0,0],
        "Extra3": [0,0,0],
    })

@pytest.fixture
def filter_layout(sample_df):
    return FilterLayout(data=sample_df, prefix="test")

def test_build_dropdown_existing_column(filter_layout):
    config = {"column": "Region", "placeholder": "Select Region"}
    dropdown_div = filter_layout.build_dropdown("region", config)
    assert isinstance(dropdown_div, html.Div)
    dropdown = dropdown_div.children
    assert isinstance(dropdown, dcc.Dropdown)
    assert dropdown.id == "test_region-dropdown"
    # Prüfen, ob Optionen korrekt sind
    labels = [opt["label"] for opt in dropdown.options]
    assert "A" in labels and "B" in labels and "C" in labels
    # Prüfen, ob Multi True
    assert dropdown.multi is True

def test_build_dropdown_missing_column(filter_layout):
    config = {"column": "NonExistingCol", "placeholder": "Select X"}
    dropdown_div = filter_layout.build_dropdown("x", config)
    dropdown = dropdown_div.children
    # Sollte Optionen aus den Spalten 6+ nehmen
    labels = [opt["label"] for opt in dropdown.options]
    expected = list(filter_layout.data.columns[6:])
    assert all(label in labels for label in expected)

def test_build_all(filter_layout):
    filter_config = {
        "region": {"column": "Region", "placeholder": "Select Region"},
        "country": {"column": "Country", "placeholder": "Select Country"}
    }
    dropdowns = filter_layout.build_all(filter_config)
    assert isinstance(dropdowns, list)
    assert len(dropdowns) == 2
    for d in dropdowns:
        assert isinstance(d, html.Div)
        assert isinstance(d.children, dcc.Dropdown)