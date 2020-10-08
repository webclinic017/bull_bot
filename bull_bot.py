# Data aqcuisition
import yfinance as yf
from rh_interface import *
from pandas_datareader import data
import pandas as pd

# Utils
from datetime import *
import numpy as np
import math
import time
from sortedcontainers import SortedKeyList

# Internal imports
from BullGraph      import *
from BullScreener   import *
from BullColors     import *
from BUI import *

# Initializing graph
bg = BullGraph(start_date=start_date, end_date=end_date)

rh_holdings = get_rh_holdings("malleyconnor@knights.ucf.edu")

# Creating the Ticker input
ticker_bar = dcc.Input(id="ticker_in", type="text", placeholder="NVDA", debounce=True)

# Initializing stock screener
bs = BullScreener(ticker_list=['NVDA', 'MSFT', 'AAPL', 'TSLA'])
#bs.get_trendlines()

# Creating dash table of rh holdings
columns = [{'name' : column, 'id' : column} for column in rh_holdings.columns]
holdings_table = dash_table.DataTable(id="holdings_table", columns=columns, data=rh_holdings.to_dict('records'))

graph_style = {'display':'inline-block', 'vertical-align' : 'top', 'margin-left' : '3vw', 'margin-top' : '3vw', 'width':'49%'}





if __name__ == "__main__":
    # Run server
    app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter