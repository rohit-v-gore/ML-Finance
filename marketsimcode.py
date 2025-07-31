""""""
"""MC2-P1: Market simulator.  		  	   		   	 		  		  		    	 		 		   		 		  

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
import pandas as pd
import datetime as dt
#Rohit Gore
from util import get_data

def author():
    return 'rgore32'
def study_group():
    return 'rgore32'



def compute_portvals(df, sd=dt.datetime(2008, 1, 1), ed=dt.datetime(2009, 12, 31),
                     start_val=1000000, commission=9.95, impact=0.005):
    dates = pd.date_range(sd, ed)
    index=0
    df['Symbol'] = df['Symbol'].apply(lambda x: x[index] if isinstance(x, list) else x)
    symbols = df['Symbol'].unique().tolist()
    vals = get_data(symbols, dates)
    flag=1
    vals.fillna(method='ffill', inplace=True)
    fill=1
    vals.fillna(method='bfill', inplace=True)
    def update_trades(trades, trade_date, symbol, order, shares, trade_price):
        cost = shares * trade_price * (fill + impact if order == 'BUY' else fill - impact)
        if order == 'BUY':
            trades.at[trade_date, 'Cash'] -= cost
            flag=1
            trades.at[trade_date, symbol] += shares
        elif order == 'SELL':
            trades.at[trade_date, symbol] -= shares
            flag=-1
            trades.at[trade_date, 'Cash'] += cost
        trades.at[trade_date, 'Cash'] -= commission
    prices = vals[symbols].copy()
    prices['Cash'] = flag
    trades = pd.DataFrame(flag-1, columns=prices.columns, index=prices.index)
    for _, row in df.iterrows():
        trade_date = pd.to_datetime(row['Date'])
        update_trades(trades, trade_date, row['Symbol'], row['Order'], row['Shares'], prices.at[trade_date, row['Symbol']])
    holdings = trades.cumsum()
    holdings['Cash'] += start_val
    portfolio_values = holdings * prices
    portvals = portfolio_values.sum(axis=flag)
    return portvals



if __name__ == "__main__":
    pass

