#Rohit Gore
import matplotlib.pyplot as plt
import datetime as dt
from indicators import Bollinger_Bands
from util import get_data
from marketsimcode import compute_portvals
from indicators import SMA_percent
from indicators import SMA

from indicators import rolling_volatility
import pandas as pd

class ManualStrategy(object):

    def __init__(self, verbose=False, impact=0.0, commission=0):
        self.impact = impact
        self.commission = commission
        self.verbose = verbose
    def author(self):
        return "rgore32"
    def study_group(self):
        return "rgore32"

    def add_evidence(self):
        pass
        return

    def testPolicy(self, symbol, sd, ed, sv=100000):
        window = 19
        entry_dates = []
        current_position = 0
        row = 0
        get_price = get_data(["JPM"], pd.date_range(sd, ed), addSPY=True, colname="Adj Close").drop(columns="SPY")
        prices = get_price[symbol]
        sym = [symbol]
        sma = SMA(get_price, window, sym)
        bollinger = Bollinger_Bands(get_price, window, sym)
        exit_dates = []

        trades = pd.DataFrame({"Date": [], "Symbol": [], "Order": [], "Shares": []})
        sma_percent = SMA_percent(get_price, window, sma, sym)
        price_volatility = rolling_volatility(get_price, window, sym)

        # Loop through prices and make decisions
        for i in range(len(prices) - 1):
            date = str(prices.index[i].date())

            # Get conditions for the current position
            conditions = define_conditions(current_position, date, bollinger, sma_percent, price_volatility, symbol)

            # Define switch cases for different current_position values
            switch = {
                0: lambda: handle_no_position(conditions, trades, date, symbol, row),
                -1: lambda: handle_short_position(conditions, trades, date, symbol, row, entry_dates,
                                                       prices.index[i]),
                1: lambda: handle_long_position(conditions, trades, date, symbol, row, exit_dates, prices.index[i])
            }
            if current_position in switch:
                current_position, row = switch[current_position]()
        if current_position == 1:
            trades.loc[row] = [prices.index[-1].date().isoformat(), symbol, "SELL", 1000]
        elif current_position == -1:
            trades.loc[row] = [prices.index[-1].date().isoformat(), symbol, "BUY", 1000]

        return trades, entry_dates, exit_dates

def handle_no_position( conditions, trades, date, symbol, row):
    if conditions["buy"]:
        trades.loc[row] = [date, symbol, "BUY", 1000]
        return 1, row + 1
    elif conditions["sell"]:
        trades.loc[row] = [date, symbol, "SELL", 1000]
        return -1, row + 1
    return 0, row

def handle_short_position(conditions, trades, date, symbol, row, entry_dates, index_date):
    if conditions["buy_full"]:
        trades.loc[row] = [date, symbol, "BUY", 2000]
        entry_dates.append(index_date.date())
        return 1, row + 1
    elif conditions["buy_partial"]:
        trades.loc[row] = [date, symbol, "BUY", 1000]
        return 0, row + 1
    return -1, row

def handle_long_position(conditions, trades, date, symbol, row, exit_dates, index_date):
    if conditions["sell_full"]:
        trades.loc[row] = [date, symbol, "SELL", 2000]
        exit_dates.append(index_date.date())
        return -1, row + 1
    elif conditions["sell_partial"]:
        trades.loc[row] = [date, symbol, "SELL", 1000]
        return 0, row + 1
    return 1, row
def define_conditions(current_position, date, bollinger, sma_percent, price_volatility, symbol):
    b = bollinger.loc[date, symbol]
    sma = sma_percent.loc[date, symbol]
    vol = price_volatility.loc[date, symbol]

    if current_position == 0:
        return {
            "buy": (b < 0.15 or sma < 0.3) and vol < -0.1,
            "sell": vol > 0.1 or (b > 0.85 and sma > 1.1)
        }

    elif current_position == -1:
        return {
            "buy_full": vol < -2.0 or b < 0.15 or sma < 0.5,
            "buy_partial": (b < 0.15 and sma < 0.4) or vol < -2.0
        }

    elif current_position == 1:
        return {
            "sell_full": b > 0.85 or vol > 2.0 or sma > 1.5,
            "sell_partial": (b > 0.8 and vol > 2.0) or sma > 1.3
        }

    return {}
if __name__ == "__main__":

    def run_strategy(sd, ed, symbol, plot_title, save_path):

        df_trades, long_points, short_points = ManualStrategy.testPolicy("self", symbol, sd, ed)

        dates = pd.date_range(sd, ed)
        prices = get_data([symbol], dates)

        # Benchmark strategy: Buy 1000 shares on the first day and sell on the last
        benchmark = pd.DataFrame(columns=["Date", "Symbol", "Order", "Shares"])
        benchmark.loc[0] = [prices.index[0].date(), symbol, "BUY", 1000]
        comms=9.95
        impact=0.005
        # Compute portfolio values
        ms_val = compute_portvals(df_trades, sd, ed, 100000, comms, impact)
        benchmark.loc[1] = [prices.index[-1].date(), symbol, "SELL", 1000]
        comms=9.95
        impact=0.005
        bench_port_val = compute_portvals(benchmark, sd, ed, 100000, comms, impact)
        ms_cr, ms_adr, ms_sddr = calculate_performance(ms_val)
        bench_cr, bench_adr, bench_sddr = calculate_performance(bench_port_val)
        print_performance(plot_title, ms_cr, ms_adr, ms_sddr, bench_cr, bench_adr, bench_sddr)
        bench_port_val /= bench_port_val.iloc[0]
        ms_val /= ms_val.iloc[0]
        plot_results(ms_val, bench_port_val, long_points, short_points, plot_title, save_path)


    def calculate_performance(port_val):
        daily_returns = port_val.pct_change().dropna()
        cr = (port_val.iloc[-1] / port_val.iloc[0]) - 1
        adr = daily_returns.mean()
        sddr = daily_returns.std()
        return cr, adr, sddr


    def print_performance(title, ms_cr, ms_adr, ms_sddr, bench_cr, bench_adr, bench_sddr):
        pass #uncomment these lines in this function to print manual strategy stats for the report

        #print(f"\n{title} Stats")
        #print(f"Manual Strategy: CR: {ms_cr:.6f}, Std Dev: {ms_sddr:.6f}, Avg Daily Return: {ms_adr:.6f}")
        #print(f"Benchmark: CR: {bench_cr:.6f}, , Std Dev: {bench_sddr:.6f}, Avg Daily Return: {bench_adr:.6f}")


    def plot_results(ms_port_val, bench_port_val, long_points, short_points, title, save_path):

        ax = ms_port_val.plot(color="red", label="Manual Strategy", figsize=(10, 6))
        bench_port_val.plot(ax=ax, color="purple", label="Benchmark")

        for date in long_points:
            ax.axvline(date, color="blue", alpha=0.75, linewidth=0.5)
        for date in short_points:
            ax.axvline(date, color="black", alpha=0.75, linewidth=0.5)

        ax.plot([], [], color="blue", linewidth=1, label="Long Entries")
        ax.plot([], [], color="black", linewidth=1, label="Short Entries")

        ax.legend(loc="upper right")
        plt.title(title)
        ax.set_xlabel("Date")
        ax.set_ylabel("Normalized Portfolio Value")
        plt.grid()
        plt.savefig(save_path)
        plt.close()
    run_strategy(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 'JPM',
                 "Manual Strategy vs Benchmark (In-Sample Stock Data)", 'images/manualStratIn.png')

    run_strategy(dt.datetime(2010, 1, 1), dt.datetime(2011, 12, 31), 'JPM',
                 "Manual Strategy vs Benchmark (Out-of-Sample Stock Data)", 'images/manualStratOut.png')