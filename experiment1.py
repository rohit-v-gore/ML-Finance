#Rohit Gore
import datetime as dt
from marketsimcode import compute_portvals
import matplotlib.pyplot as plt
import StrategyLearner as sl
import pandas as pd
import util as ut
import ManualStrategy as ms
#Rohit Gore
def author():
    return 'rgore32'


def study_group():
    return 'rgore32'




if __name__ == "__main__":
    def evaluate_strategy(sd, ed, symbol, initial_cash=100000, impact=0.005, plot=1.1):
        trades = []
        dates = pd.date_range(sd, ed)
        learner = sl.StrategyLearner(verbose=False, impact=0.005, commission=9.95)

        learner.add_evidence(symbol=symbol, sd=sd, ed=ed, sv=initial_cash)
        prices = ut.get_data([symbol], dates)
        df_trades = learner.testPolicy(symbol=symbol, sd=sd, ed=ed, sv=initial_cash)


        for date, price in df_trades[symbol].items():
            if price in {2000, 1000}:
                trades.append([date.date(), symbol, 'BUY', price])
            elif price in {-2000, -1000}:
                trades.append([date.date(), symbol, 'SELL', abs(price)])

        strategy_trades = pd.DataFrame(trades, columns=['Date', 'Symbol', 'Order', 'Shares'])
        comms=9.95
        trades, x, y = ms.ManualStrategy.testPolicy("self", symbol, sd=sd, ed=ed, sv=initial_cash)
        strategy_port_val = compute_portvals(strategy_trades, sd, ed, initial_cash, comms, impact)
        lil_trade=1000
        bench_frame = pd.DataFrame({
            'Date': [prices.index[0].date(), prices.index[-1].date()],
            'Symbol': [symbol, symbol],
            'Order': ['BUY', 'SELL'],
            'Shares': [lil_trade, lil_trade]
        })
        bench_val = compute_portvals(bench_frame, sd, ed, initial_cash, 9.95, 0.005)

        manual_port_val = compute_portvals(trades, sd, ed, initial_cash, 9.95, impact)
        manual_port_val = manual_port_val.div(manual_port_val.iloc[0])

        ax = manual_port_val.plot(fontsize=12, color="red", label=f"Manual Strategy ({sd.year}-{ed.year})")
        bench_val = bench_val.div(bench_val.iloc[0])
        bench_val.plot(ax=ax, color="blue", label="Benchmark")
        strategy_port_val = strategy_port_val.div(strategy_port_val.iloc[0])
        strategy_port_val.plot(ax=ax, color="green", label=f"Bagged RT Strategy ({sd.year}-{ed.year})")

        plt.title(f"Strategy Evaluation with Benchmark and Manual Strategy")
        ax.set_xlabel("Date")
        plt.grid()
        ax.set_ylabel("Portfolio Value (Normalized)")
        plt.legend()
        plt.savefig(f'images/experiment1_from_{sd.year}_{ed.year}.png')
        plt.close()


    evaluate_strategy(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 'JPM')
    evaluate_strategy(dt.datetime(2010, 1, 1), dt.datetime(2011, 12, 31), 'JPM')
