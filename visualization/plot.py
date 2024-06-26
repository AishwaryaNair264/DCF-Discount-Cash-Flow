"""
Quick visualization toolkit. I'd like to build this out to be decently powerful
in terms of enabling quick interpretation of DCF related data.
"""

import sys

import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append('..')
from modeling.data import *

sns.set()
sns.set_context('paper')


def visualize(dcf_prices, current_share_prices, regress = True):
    # TODO: implement
    return NotImplementedError


def visualize_bulk_historicals(dcfs, ticker, condition, apikey):
    dcf_share_prices = {}
    variable = list(condition.keys())[0]
    
    #TODO: make this more eloquent for handling the plotting of multiple condition formats
    try:
        conditions = [str(cond) for cond in list(condition.values())[0]]
    except IndexError:
        print(condition)
        conditions = [condition['Ticker']]

    for cond in conditions:
        dcf_share_prices[cond] = {}
        years = dcfs[cond].keys()
        for year in years:
            dcf_share_prices[cond][year] = dcfs[cond][year]['share_price']

    for cond in conditions:
        plt.plot(list(dcf_share_prices[cond].keys())[::-1], 
                 list(dcf_share_prices[cond].values())[::-1], label = cond)

    historical_stock_prices = get_historical_share_prices(
        ticker=ticker,
        dates=list(dcf_share_prices[list(dcf_share_prices.keys())[0]].keys())[::-1],
        apikey=apikey)
    plt.plot(list(historical_stock_prices.keys()),
             list(historical_stock_prices.values()), label = '${} over time'.format(ticker))

    plt.xlabel('Date')
    plt.ylabel('Share price ($)')
    plt.legend(loc = 'upper right')
    plt.title('$' + ticker + '  ')
    plt.savefig('imgs/{}_{}.png'.format(ticker, list(condition.keys())[0]))
    plt.show()


def visualize_historicals(dcfs):
    pass

    dcf_share_prices = {}
    for k, v in dcfs.items():
        dcf_share_prices[dcfs[k]['date']] = dcfs[k]['share_price']

    xs = list(dcf_share_prices.keys())[::-1]
    ys = list(dcf_share_prices.values())[::-1]

    plt.scatter(xs, ys)
    plt.show()
