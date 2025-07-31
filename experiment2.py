import pandas as pd
import StrategyLearner as sl
import datetime as dt
import matplotlib.pyplot as plt
from marketsimcode import compute_portvals
import util as ut
#Rohit Gore
def author():
    return "rgore32"
def study_group():
    return "rgore32"


if __name__ == "__main__":
    symbol = ['JPM']
    impact_tests = [0.020, 0.011, 0.000]
    sd = dt.datetime(2008, 1, 1)
    port_vals = []
    ed = dt.datetime(2009, 12, 31)
    dates = pd.date_range(sd, ed)

    prices_all = ut.get_data(symbol, dates)
    for impact in impact_tests:
        learner = sl.StrategyLearner(verbose=False, impact=impact)
        learner.add_evidence(symbol="JPM", sd=sd, ed=ed, sv=100000)
        test = learner.testPolicy(symbol="JPM", sd=sd, ed=ed, sv=100000)

        # Create trade dataframe
        trades = pd.DataFrame(columns=['Date', 'Symbol', 'Order', 'Shares'])

        action_map = {
            2000: ('BUY', 2000),
            1000: ('BUY', 1000),
            -2000: ('SELL', 2000),
            -1000: ('SELL', 1000)
        }

        # Process the trade data
        for i in range(test.shape[0]):
            date = str(test.index[i].date())
            price = test.loc[date, 'JPM']

            if price in action_map:
                order, shares = action_map[price]
                trade_entry = {'Date': date, 'Symbol': 'JPM', 'Order': order, 'Shares': shares}
                trades = pd.concat([trades, pd.DataFrame([trade_entry])], ignore_index=True)

        st_trades = trades
        st_val = compute_portvals(st_trades, sd, ed, 100000, 0, impact)
        port_vals.append(st_val)
    num_trades = []
    normalized_port_vals = [pv / pv.iloc[0] for pv in port_vals]
    labels = ["SL - impact = {}".format(impact) for impact in impact_tests]

    # Plot portfolio values
    sec_plot = normalized_port_vals[0].plot(color="black", label=labels[0])
    for i in range(1, len(normalized_port_vals)):
        normalized_port_vals[i].plot(ax=sec_plot, label=labels[i])

    plt.title("Experiment 2 - Impact Metrics")
    sec_plot.set_xlabel("Date")
    sec_plot.set_ylabel("Portfolio Value")
    plt.legend()
    plt.grid()
    plt.savefig("images/experiment2.1.png")
    plt.close()


    # Loop through each strategy and impact fee
    for impact in impact_tests:
        learner = sl.StrategyLearner(verbose=False, impact=impact)
        learner.add_evidence(symbol="JPM", sd=sd, ed=ed, sv=100000)
        test = learner.testPolicy(symbol="JPM", sd=sd, ed=ed, sv=100000)

        # Create trade dataframe
        trades = pd.DataFrame(columns=['Date', 'Symbol', 'Order', 'Shares'])

        action_map = {
            2000: ('BUY', 2000),
            1000: ('BUY', 1000),
            -2000: ('SELL', 2000),
            -1000: ('SELL', 1000)
        }

        # Process the trade data
        for i in range(test.shape[0]):
            date = str(test.index[i].date())
            price = test.loc[date, 'JPM']

            if price in action_map:
                order, shares = action_map[price]
                trade_entry = {'Date': date, 'Symbol': 'JPM', 'Order': order, 'Shares': shares}
                trades = pd.concat([trades, pd.DataFrame([trade_entry])], ignore_index=True)
        num_trades.append(len(trades))

    # Create a bar plot for the number of trades
    plt.figure(figsize=(8, 6))
    plt.bar(labels, num_trades, color='darkblue')
    plt.title("Number of Trades per Strategy Learner (Different Impact Values)")
    plt.xlabel("Strategy Learner (Impact Fees)")
    plt.ylabel("Number of Trades")
    plt.xticks(rotation=45)
    plt.ylim(150, 170)
    plt.tight_layout()
    plt.savefig("images/experiment2_trades.png")
    plt.close()