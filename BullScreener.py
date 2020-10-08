import numpy as np
import pandas as pd
from datetime import date, datetime
import yfinance as yf
from pandas_datareader import data


from TimeUtils import *


# TODO: Remove this
import matplotlib.pyplot as plt



class BullScreener(object):
    """
    BullScreener selects from a list of prospective stock tickers, and screens them for various indicators.
    """
    def __init__(self, sector=None, ticker_list=None, timeframe=5):
        self.nyse   = pd.read_csv('tickers/nyse.csv')

        if (sector):
            self.screen_list = list(self.nyse['Symbol'][~(self.nyse['Symbol'] == '') & self.nyse['industry'] == industry])
        else:
            self.screen_list = list(self.nyse['Symbol'][~(self.nyse['Symbol'] == '')])

        if (ticker_list):
            self.screen_list = ticker_list


        # Gets started date based on input
        day   = date.today().day
        month = ((date.today().month - timeframe) % 12)
        year  = date.today().year  
        if (timeframe >= month):
            year -= 1
        date_string = f'%d %s %d' % (day, months[month-1], year)
        start = datetime.strptime(date_string, "%d %B %Y")

        # Gets yahoo finance data for selected stock tickers
        self.historical = {}
        self.financials = {}
        for ticker in self.screen_list:
            self.historical[ticker] = data.DataReader(ticker, "yahoo", start, date.today())
            self.financials[ticker] = yf.Ticker(ticker)

    def get_trendlines(self):
        self.trendlines = {}
        x = np.linspace(0,1, len(self.historical[self.screen_list[0]]))
        for ticker in self.screen_list:
            y = self.rescale_data(list(self.historical[ticker]['Close']))
            turning_points = self.detect_turning_points(y)
            plt.plot(x, y)
            edge_x_inds = np.arange(0,len(y))[turning_points != 0]
            edges_x = x[turning_points == 1]
            edges_y = y[turning_points == 1]
            
            # rho = x*cos(theta) + y*sin(theta)
            thetas = np.deg2rad(np.linspace(-90, 90, len(edges_x)))
            print(thetas)
            cos_thetas = np.cos(thetas)
            sin_thetas = np.sin(thetas)
            rhos = np.vstack([np.add(np.multiply(edges_x[i], cos_thetas), np.multiply(edges_y[i], sin_thetas)) for i in range(len(edges_x))]).T

            hough_space = pd.DataFrame(np.around(rhos, 2), index=thetas)     
            hough_space.plot(legend=None)

            unique_rhos = np.unique(hough_space)            
            def accumulator(row):
                rhos, counts = np.unique(row, return_counts=True)
                s=pd.Series(0, index=unique_rhos)
                s[rhos] = counts
                return s

            print(f"LEN == %d" % (len(y)))
            accumulated = hough_space.apply(accumulator, axis=1)
            accumulated_index = np.around(accumulated.index, 4)

            # Displaying heatmap
            fig = plt.figure(figsize=(8,6))
            sns.heatmap(accumulated)
            plt.show()

            time_value_lookup_table = {}
            y = pd.Series(y)
            for index, rho in np.ndenumerate(rhos):
                k     = (thetas[index[0]], rho)
                time  = y.index[edge_x_inds[index[1]]]
                value = edges_y[index[1]]

                if k in time_value_lookup_table:
                    time_value_lookup_table[k].add((time, value))
                else:
                    time_value_lookup_table[k]=\
                        SortedKeyList([(time, value)], key=lambda x: x[0])

            
            theta_indices, rho_indices =\
                np.unravel_index(np.argsort(accumulated.values, axis=None), accumulated.shape)

            touches   = []
            distances = []
            points    = []

            for i in range(len(theta_indices)):
                tp = (thetas[theta_indices[i]], unique_rhos[rho_indices[i]])
                if tp in time_value_lookup_table:
                    p = time_value_lookup_table[tp]
                    if len(p) > 1:
                        touches.append(len(p))
                        distances.append(p[-1][0] - p[0][0] if len(p) > 1 else 0)
                        points.append(p)

            ranked_lines = pd.DataFrame(
                {
                    "touches" : touches,
                    "distances" : distances,
                    "points" : points
                },
                index=range(len(points), 0, -1)
            )

            lines = ranked_lines[ranked_lines["distances"] > timedelta(days=30)]
            y.plot(figsize=(20,8))

            for i, r in lines.iterrows():
                x = r["points"][0][0], r["points"][-1][0]
                y = r["points"][0][1], r["points"][-1][1]
                plt.plot(x, y)

            plt.show()

            print(ranked_lines[-10:0])
             
    
    def rescale_data(self, arr):
        """
        Normalizes data in array between 0 and 1

        Args:
            arr (list): Array to be scaled. Defaults to [].

        Returns:
            (list): new scaled array
        """
        minval = np.min(arr)
        maxval = np.max(arr)
        scaled_arr = np.subtract(arr, minval)
        scaled_arr = np.divide(scaled_arr, maxval-minval)
        return scaled_arr

    def detect_turning_points(self, y, period=5):
        """
            Returns a list of indices, containing the inflection points of y.
        """
        turning_points = np.zeros(len(y))
        for i in range(math.ceil(period/2), len(turning_points)-math.ceil(period/2)):
            turning_points[i] = self.turning_point(y[i-math.ceil(period/2) : i+math.ceil(period/2)+1 :])

        return turning_points

    def turning_point(self, sub_arr):
        """
        Finds a V or an A turning point in the sub array

        Args:
            sub_arr (list): Array possibly containing a turning point.

        Returns:
            (int): +1 for V, -1 for A, or 0 for no turning point.
        """
        avg = np.mean(sub_arr)

        # Found a bullish inflection point
        if sub_arr[0] > avg and sub_arr[-1] > avg:
            return 1
        # Found a bearish inflection point
        elif sub_arr[0] < avg and sub_arr[-1] < avg:
            return -1
        # No inflection point
        else:
            return 0