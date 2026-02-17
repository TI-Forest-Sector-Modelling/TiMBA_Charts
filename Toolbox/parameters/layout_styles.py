outer_card_under_header={
    "height": "calc(100vh - 175px)",
    "display": "flex",
    "flexDirection": "column",
    "padding": "0px",
    "overflow": "hidden"
}

filter_card_background={
    "backgroundColor": "#f8f9fa",
    "border": "1px solid #dee2e6",
    "borderRadius": "1px",
    "flexShrink": "0"
}

filter_inner_card={
    "display": "flex",
    "gap": "10px",
    "alignItems": "flex-end",
    "width": "100%",
}

plot_card_background={
    "display": "grid",
    "gridTemplateColumns": "1fr 1.75fr 1fr",
    "gridTemplateRows": "1fr 1fr",
    "gap": "15px",
    "padding": "15px",
    "backgroundColor": "#f8f9fa",
    "border": "1px solid #dee2e6",
    "borderRadius": "6px",
    "marginTop": "10px",
    "marginBottom": "10px",
    "flexGrow": "1",
    "minHeight": "0",
    "height": "100%"
}

#---
# span plot over 2 grid cells
#---
main_plot_card={
    "gridColumn": "2",
    "gridRow": "1 / span 2",
    "height": "100%", 
    "minHeight": "0",  
}