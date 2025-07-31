""""""
"""  		  	   		 	 	 			  		 			     			  	 
Template for implementing StrategyLearner  (c) 2016 Tucker Balch  		  	   		 	 	 			  		 			     			  	 

Copyright 2018, Georgia Institute of Technology (Georgia Tech)  		  	   		 	 	 			  		 			     			  	 
Atlanta, Georgia 30332  		  	   		 	 	 			  		 			     			  	 
All Rights Reserved  		  	   		 	 	 			  		 			     			  	 

Template code for CS 4646/7646  		  	   		 	 	 			  		 			     			  	 

Georgia Tech asserts copyright ownership of this template and all derivative  		  	   		 	 	 			  		 			     			  	 
works, including solutions to the projects assigned in this course. Students  		  	   		 	 	 			  		 			     			  	 
and other users of this template code are advised not to share it with others  		  	   		 	 	 			  		 			     			  	 
or to make it available on publicly viewable websites including repositories  		  	   		 	 	 			  		 			     			  	 
such as github and gitlab.  This copyright statement should not be removed  		  	   		 	 	 			  		 			     			  	 
or edited.  		  	   		 	 	 			  		 			     			  	 

We do grant permission to share solutions privately with non-students such  		  	   		 	 	 			  		 			     			  	 
as potential employers. However, sharing with other current or future  		  	   		 	 	 			  		 			     			  	 
students of CS 7646 is prohibited and subject to being investigated as a  		  	   		 	 	 			  		 			     			  	 
GT honor code violation.  		  	   		 	 	 			  		 			     			  	 

-----do not edit anything above this line---  		  	   		 	 	 			  		 			     			  	 

Student Name: Rohit Gore 		  	   		 	 	 			  		 			     			  	 
GT User ID: rgore32	  	   		 	 	 			  		 			     			  	 
GT ID: 903574004			  	   		 	 	 			  		 			     			  	 
"""
#Rohit Gore
import BagLearner as bl
import numpy as np
from indicators import Bollinger_Bands
import util as ut
import RTLearner as rt

from indicators import rolling_volatility
import datetime as dt
from indicators import SMA



import pandas as pd

class StrategyLearner(object):

    def author(self):
        return 'rgore32'
    def study_group(self):
        return "rgore32"

    def __init__(self, verbose=False, impact=0.0, commission=0):
        self.impact = impact
        self.commission = commission
        self.learner = bl.BagLearner(
            learner=rt.RTLearner, kwargs={"leaf_size": 5}, bags=25, boost=False, verbose=False)
        self.verbose = verbose


    def add_evidence(self, symbol="AAPL", sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 1, 1),
                     sv=10000):
        date_range = pd.date_range(sd, ed)
        window = 5
        symbols = [symbol]
        price_data = ut.get_data(symbols, date_range)[symbols]
        volatility_values = rolling_volatility(price_data, window, symbols)


        sma_values = SMA(price_data, window, symbols)
        bollinger_bands = Bollinger_Bands(price_data, window, symbols)
        future_returns = (price_data.shift(-window) - price_data) / price_data
        indicator_data = pd.DataFrame({
            'SMA': sma_values[symbol],
            'BBA': bollinger_bands[symbol],
            'VOL': volatility_values[symbol]
        }).fillna(0)[:-window]

        X = indicator_data.values

        Y = np.where(
            future_returns[symbol] > self.impact, 1,
            np.where(
                future_returns[symbol] < -self.impact, -1,
                0
            )
        )[:-window]

        self.learner.add_evidence(X, Y)

    def handle_position(self, position_flag, prediction, trades, index):
        # Define actions for each position_flag state in a dictionary
        actions = {
            0: self.handle_neutral_position,
            1: self.handle_long_position,
            -1: self.handle_short_position
        }

        position_flag, trades = actions[position_flag](position_flag, prediction, trades, index)

        return position_flag, trades

    def handle_neutral_position(self, position_flag, prediction, trades, index):
        pred_val = 0
        match prediction:
            case p if p > pred_val:
                position_flag = 1
                trades.iloc[index, 0] = 1000
            case p if p < pred_val:
                position_flag = -1
                trades.iloc[index, 0] = -1000
            case _:
                pass
        return position_flag, trades

    def handle_long_position(self, position_flag, prediction, trades, index):
        pred_val = 0
        match prediction:
            case p if p < pred_val:
                position_flag = -1
                trades.iloc[index, 0] = -2000
            case p if p == pred_val:
                trades.iloc[index, 0] = -1000
                position_flag = pred_val  # Neutral
            case _:
                pass
        return position_flag, trades

    def handle_short_position(self, position_flag, prediction, trades, index):
        pred_val = 0
        match prediction:
            case p if p > pred_val:
                position_flag = 1
                trades.iloc[index, 0] = 2000

            case p if p == pred_val:
                position_flag = 0
                trades.iloc[index, 0] = 1000
                 # Neutral
            case _:
                pass
        return position_flag, trades

    def testPolicy(self, symbol="AAPL", sd=dt.datetime(2009, 1, 1), ed=dt.datetime(2010, 1, 1), sv=10000):
        date_range = pd.date_range(sd, ed)
        window = 10
        symbols = [symbol]
        price_data = ut.get_data(symbols, date_range)[symbols]
        sma_values = SMA(price_data, window, symbols)
        data=0
        volatility_values = rolling_volatility(price_data, window, symbols)
        bollinger_bands = Bollinger_Bands(price_data, window, symbols)
        indicator_data = pd.DataFrame({
            'SMA': sma_values[symbol],
            'BBA': bollinger_bands[symbol],
            'VOL': volatility_values[symbol]
        }).fillna(data)

        X_feat = indicator_data.values

        # Construct trades DataFrame
        trades = pd.DataFrame(data, index=price_data.index, columns=[symbol])
        position_flag = data  # 0: Neutral, 1: Long, -1: Short
        Y = self.learner.query(X_feat)  # Get predictions from learner
        for i in range(len(Y) - 1):
            position_flag, trades = self.handle_position(position_flag, Y[i], trades, i)
        trades = self.close_final_position(position_flag, trades, len(Y))

        return trades


    def close_final_position(self, position_flag, trades, data_length):
        match position_flag:
            case -1:
                trades.iloc[data_length - 1, 0] = 1000
            case 1:
                trades.iloc[data_length - 1, 0] = -1000

        return trades



if __name__ == "__main__":
    print("One does not simply think up a strategy")



