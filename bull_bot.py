import yfinance as yf
import time
import matplotlib
import matplotlib.pyplot as plt
import seaborn
import pandas as pd
from pandas_datareader import data
from datetime import datetime
import plotly.graph_objects as go
import math
from IPython.display import display, HTML
import dash
import dash_core_components as dcc
import dash_html_components as html
import robin_stocks as rh
from dash.dependencies import Input, Output

start_date = datetime(2016, 1, 1)
end_date   = datetime(2020, 7, 27)

colors = {
    "text" : "#7FDBFF",
    "background" : "#63995c"
}



# ROBIN HOOD

# Grabs password
passfile = open("rh_pass.txt", "r")
password = passfile.read()
passfile.close()

rh.authentication.login(username="malleyconnor@knights.ucf.edu", password=password)

securities = rh.profiles.load_security_profile()
portfolio  = rh.profiles.load_portfolio_profile()
holdings   = rh.account.build_holdings()

security_list = ""
for security in holdings:
    this_security = f"%s -- %s\n" % (holdings[security]["name"], holdings[security]["price"])
    security_list = f"%s%s" % (security_list, this_security)

security_list = f"<b>%s</b>" % security_list




def createFig(ticker="NVDA"): 
    """
        createFig(ticker)
        =================
            Description: Creates historical candlestick graph for the input stock ticker.

            Inputs:
                - ticker (str): string representing a stock ticker (e.g. NVDA, AMD, FCEL, etc...)

            Output:
                - None

            Return(s):
                - fig (go.Figure): figure object
    """
    print(f"%s : %s" % (ticker, str(type(ticker))))
    df = data.DataReader(ticker, "yahoo", start_date, end_date )
    df.reset_index(inplace=True, drop=False)

    # Creating graph
    fig = go.Figure(
        data=[go.Candlestick(x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'])])

    ############################
    # Styling the graph
    fig.layout = dict({
        "title_x" : 0.5,
        "xaxis_title" : "<b>Date</b>",
        "yaxis_title" : "<b>Price</b>",
        "paper_bgcolor": colors["background"],
        "font" : dict(
            color="#7f7f7f",
            size=18
        )
    })


    fig.update_xaxes(
        rangebreaks=[dict(bounds=["sat", "mon"])],
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    return fig, df



app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

# Creating the Ticker input
ticker_bar = dcc.Input(id="ticker_in", type="text", placeholder="NVDA", debounce=True)


# Initial Configuration
fig, df = createFig("NVDA")
app.layout = html.Div(
    style={
        "background-color" : "#63995c"
    },
    children=[
        dcc.Graph(id="main_graph", figure=fig),
        html.Div(
            children=security_list, 
            style={
                "color" : colors["text"]
            }
        ),
        ticker_bar,
        html.Div(id="ticker_out")
    ]
)

# Rendering the ticker input for the graph
@app.callback(Output("main_graph", "figure"),
[Input("ticker_in", "value")])
def ticker_render(vals="NVDA"):
    if (vals == None):
        fig, df = createFig("NVDA")
        return fig

    fig, df = createFig(vals)
    return fig



if __name__ == "__main__":
    # Run server
    app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter