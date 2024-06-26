"""
Utilizing financialmodelingprep.com for their free-endpoint API to gather company financials.
"""

from urllib.request import urlopen
import json, traceback


def get_api_url(requested_data, ticker, period, apikey):
    if period == 'annual':
        url = 'https://financialmodelingprep.com/api/v3/{requested_data}/{ticker}?apikey={apikey}'.format(
            requested_data=requested_data, ticker=ticker, apikey=apikey)
    elif period == 'quarter':
        url = 'https://financialmodelingprep.com/api/v3/{requested_data}/{ticker}?period=quarter&apikey={apikey}'.format(
            requested_data=requested_data, ticker=ticker, apikey=apikey)
    else:
        raise ValueError("invalid period " + str(period))
    return url


def get_jsonparsed_data(url):
    try: response = urlopen(url)
    except Exception as e:
        print(f"Error retrieving {url}:")
        try: print("\t%s"%e.read().decode())
        except: pass
        raise
    data = response.read().decode('utf-8')
    json_data = json.loads(data)
    if "Error Message" in json_data:
        raise ValueError("Error while requesting data from '{url}'. Error Message: '{err_msg}'.".format(
            url=url, err_msg=json_data["Error Message"]))
    return json_data


def get_EV_statement(ticker, period='annual', apikey=''):
    url = get_api_url('enterprise-value', ticker=ticker, period=period, apikey=apikey)
    return get_jsonparsed_data(url)


def get_income_statement(ticker, period='annual', apikey=''):
    url = get_api_url('financials/income-statement', ticker=ticker, period=period, apikey=apikey)
    return get_jsonparsed_data(url)


def get_cashflow_statement(ticker, period='annual', apikey=''):
    url = get_api_url('financials/cash-flow-statement', ticker=ticker, period=period, apikey=apikey)
    return get_jsonparsed_data(url)


def get_balance_statement(ticker, period='annual', apikey=''):
    url = get_api_url('financials/balance-sheet-statement', ticker=ticker, period=period, apikey=apikey)
    return get_jsonparsed_data(url)


def get_stock_price(ticker, apikey=''):
    url = 'https://financialmodelingprep.com/api/v3/stock/real-time-price/{ticker}?apikey={apikey}'.format(
        ticker=ticker, apikey=apikey)
    return get_jsonparsed_data(url)


def get_batch_stock_prices(tickers, apikey=''):
    prices = {}
    for ticker in tickers:
        prices[ticker] = get_stock_price(ticker=ticker, apikey=apikey)['price']

    return prices


def get_historical_share_prices(ticker, dates, apikey=''):
    prices = {}
    for date in dates:
        try: date_start, date_end = date[0:8] + str(int(date[8:]) - 2), date
        except:
            print(f"Error parsing '{date}' to date.")
            print(traceback.format_exc())
            continue
        url = 'https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={date_start}&to={date_end}&apikey={apikey}'.format(
            ticker=ticker, date_start=date_start, date_end=date_end, apikey=apikey)
        try:
            prices[date_end] = get_jsonparsed_data(url)['historical'][0]['close']
        except IndexError:
            try:
                prices[date_start] = get_jsonparsed_data(url)['historical'][0]['close']
            except IndexError:
                print(date + ' ', get_jsonparsed_data(url))

    return prices


if __name__ == '__main__':

    ticker = 'AAPL'
    apikey = '<DEMO>'
    data = get_cashflow_statement(ticker=ticker, apikey=apikey)
    print(data)
