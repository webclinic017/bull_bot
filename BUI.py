import dash
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from IPython.display import display, HTML
from dash.dependencies import Input, Output
import requests

# TODO: Change to CSS
from BullColors import colors
from bull_bot import *

app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div(
    style={
        "background-color" : colors["page_background"]
    },
    children=[
        dcc.Graph(id="main_graph", figure=bg.fig, style=graph_style),
        html.Div(
            children=holdings_table,
            style={'display':'inline-block', 'vertical_align':'right', 'margin-left':'3vw', 'margin-right':'3vw', 'margin-top':'10vw', 'width':'40%'}
        ),
        ticker_bar,
        html.Div(id="ticker_out")
    ]
)

# Rendering the ticker input for the graph
@app.callback(Output("main_graph", "figure"),
[Input("ticker_in", "value")])
def ticker_render(ticker="NVDA"):
    if (ticker == None):
        bg.ticker = "NVDA"
        fig = bg.createFig()
        fig, historical = bg.styleFig()
        return fig

    bg.ticker = ticker
    fig = bg.createFig()
    fig, historical = bg.styleFig()
    return fig