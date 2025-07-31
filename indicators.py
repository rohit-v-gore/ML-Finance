import pandas as pd
from util import get_data
import datetime as dt
#Rohit Gore
def author():
    return "rgore32"
def study_group():
    return "rgore32"

def StochasticOscillator(val, window=14, stock="AAPL"):
    low_min = val.rolling(window=window).min()
    high_max = val.rolling(window=window).max()
    price = val[stock]

    # %K calculation
    percent_k = 100 * ((val- low_min) / (high_max - low_min))

    # %D calculation (3-day simple moving average of %K)
    percent_d = percent_k.rolling(window=3).mean()

    return pd.DataFrame({'%K': percent_k, '%D': percent_d}) #percent D is the real results vector

def SMA(val, window, stock):
    price = val[stock]
    lookback=window
    sma = price.rolling(window=lookback).mean()
    return sma
def Bollinger_Bands(val, window, stock):
    moving_av = SMA(val, window,stock)
    price = val[stock]
    std = price.rolling(window=window).std()
    width =std
    bollinger = (price - moving_av) / (2 * width)
    return bollinger
def rolling_volatility(val, window, stock):
    price = val[stock]
    next_price=price
    rv = next_price.rolling(window=window).std()
    return rv
def momentum(val, window=10, stock=None):
    momentum = (val/ val.shift(window)) - 1
    price = val[stock]
    return momentum



# Example of how to run all indicators:
def run_all_indicators(val):
    sma = SMA(val, 10,"AAPL")
    bollinger_bands = Bollinger_Bands(val)
    Momentum = momentum(val, 10,"AAPL")
    rv = rolling_volatility(val, 10,"AAPL")
    SO = StochasticOscillator(val, 14, "AAPL")

    return {
        'SMA': sma,
        'Bollinger Bands': bollinger_bands,
        'Momentum': Momentum,
        'Rolling Volatility': rv,
        'Stohastic Oscillator': SO
    } #includes all the real results vectors for the following indicator functions
def SMA_percent(val, window, sma, symbols):
    sma = sma.copy()
    validm = sma.notna()
    sma[validm] = val[validm] / sma[validm]
    return sma


# Example usage
if __name__ == "__main__":
    symbol = 'JPM'
    start_date = dt.datetime(2010, 1, 1)
    end_date = dt.datetime(2020, 12, 31)
    dates = pd.date_range(start_date, end_date)
    val = get_data([symbol], dates)[symbol]
    printer=run_all_indicators(val)