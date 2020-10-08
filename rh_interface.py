import pandas as pd
import robin_stocks as rh

# ROBIN HOOD
def get_rh_holdings(username=""):
    """
    get_rh_holdings(username)
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