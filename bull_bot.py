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
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import robin_stocks as rh
from dash.dependencies import Input, Output
import numpy as np


start_date = datetime(2016, 1, 1)
end_date   = datetime(2020, 7, 27)

colors = {
    "text" : "#FFFFFF",
    "background" : "#63995c"
}

class BullGraph(object):
    # TODO: Change to use relative dates from current date
    def __init__(self, ticker="NVDA", start_date=start_date, end_date=end_date):
        self.start_date = start_date
        self.end_date   = end_date
        self.ticker     = ticker
        self.createFig()

    def createFig(self): 
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
        try:
            self.historical = data.DataReader(self.ticker, "yahoo", self.start_date, self.end_date )
        except IOError:
            self.historical = data.DataReader("NVDA", "yahoo", self.start_date, self.end_date )

        self.historical.reset_index(inplace=True, drop=False)

        # Creating graph
        self.fig = go.Figure(
            data=[go.Candlestick(x=self.historical['Date'],
            open=self.historical['Open'],
            high=self.historical['High'],
            low=self.historical['Low'],
            close=self.historical['Close'])])

        return self.fig

    def styleFig(self):
        if not self.fig:
            # Creating graph
            self.fig = go.Figure(
                data=[go.Candlestick(x=historical['Date'],
                open=self.historical['Open'],
                high=self.historical['High'],
                low=self.historical['Low'],
                close=self.historical['Close'])])


        # Styling the graph
        self.fig.layout = dict({
            "title_x" : 0.5,
            "xaxis_title" : "<b>Date</b>",
            "yaxis_title" : "<b>Price</b>",
            "paper_bgcolor": colors["background"],
            "font" : dict(
                color=colors["text"],
                size=18
            )
        })


        self.fig.update_xaxes(
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

        return self.fig, self.historical



# ROBIN HOOD
# Grabs password
def get_rh_holdings(username=""):
    """
    rh_login(username)
    ==================
        Description:    Logs into robinhood with the specified username and password, 
                        and grabs data of current positions

        Input(s):
            - username (str): username/email of robinhood account

        Output(s):
            - None

        Return(s):
            - security_list (str): String displaying current positions
    """
    passfile = open("rh_pass.txt", "r")
    password = passfile.read()
    passfile.close()

    rh.authentication.login(username="malleyconnor@knights.ucf.edu", password=password)

    securities = rh.profiles.load_security_profile()
    portfolio  = rh.profiles.load_portfolio_profile()
    holdings   = rh.account.build_holdings()

    # Getting holdings data from RobinHood
    holdings_data = {}
    tickers = holdings.keys()
    values          = {} 
    shares          = {}
    equities        = {}
    changes         = {}
    percent_changes = {}
    for ticker in tickers:
        this_stock = holdings[ticker]
        values[ticker]          = this_stock['price']
        shares[ticker]          = this_stock['quantity']
        equities[ticker]        = this_stock['equity']
        percent_changes[ticker] = this_stock['percent_change']
        changes[ticker]         = this_stock['equity_change']

        holdings_data[ticker] = {
            'Ticker'         : ticker,
            'Price'          : this_stock['price'],
            'Shares'         : this_stock['quantity'],
            'Percent Change' : this_stock['percent_change'],
            'Equity'         : this_stock['equity'],
            'Change'         : this_stock['equity_change']
        }



    # Creating holdings data
    rh_holdings = pd.DataFrame.from_dict(
        data=holdings_data,
        orient='index', 
        columns=['Ticker', 'Price', 'Shares', 'Percent Change', 'Equity', 'Change']
    )

    return rh_holdings



app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

# Initializing graph
start_date = datetime(2016, 1, 1)
end_date   = datetime(2020, 7, 27)
bg = BullGraph(start_date=start_date, end_date=end_date)

rh_holdings = get_rh_holdings("malleyconnor@knights.ucf.edu")

# Creating the Ticker input
ticker_bar = dcc.Input(id="ticker_in", type="text", placeholder="NVDA", debounce=True)



# Creating dash table of rh holdings
columns = [{'name' : column, 'id' : column} for column in rh_holdings.columns]
holdings_table = dash_table.DataTable(id="holdings_table", columns=columns, data=rh_holdings.to_dict('records'))

graph_style = {'display':'inline-block', 'vertical-align' : 'top', 'margin-left' : '3vw', 'margin-top' : '3vw', 'width':'49%'}

app.layout = html.Div(
    style={
        "background-color" : "#63995c"
    },
    children=[
        dcc.Graph(id="main_graph", figure=bg.fig, style=graph_style),
        html.Div(
            children=holdings_table,
            style={'display':'inline-block', 'vertical_align':'right', 'margin-left':'3vw', 'margin-right':'3vw', 'margin-top':'3vw', 'width':'40%'}
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



if __name__ == "__main__":
    # Run server
    app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter