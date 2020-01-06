##########################################################################

# BINANCE API Connection
# Documentation ref can be found at: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md

##########################################################################

import time, json, requests, os, sys
from urllib.parse import urljoin, urlencode
from sqlalchemy import create_engine, Table, MetaData, text, select
import pandas as pd
import numpy as np

from utilities import obtain_env_variable

API_KEY = obtain_env_variable('BINANCE_API_KEY', 'BINANCE_API_KEY')
BASE_URL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': API_KEY
}

class BinanceException(Exception):
    def __init__(self, status_code, data):

        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"

        # Python 2.x
        # super(BinanceException, self).__init__(message)
        super().__init__(message)

##########################################################################
def get_status_code():
    """
    get servertime and check if connection works.
    weight is 1

    """
    PATH =  '/api/v1/time'
    params = None
    timestamp = int(time.time() * 1000)
    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, params=params)
    if r.status_code == 200:
        # uncomment if I want the raw API response
        #print(json.dumps(r.json(), indent=2))
        data = r.json()
        diff= timestamp - data['serverTime']
        #print(f"diff={timestamp - data['serverTime']}ms")
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
        diff='API CALL DID NOT WORK'
    return diff

#diff=get_status_code()
#print(diff)
##########################################################################
def get_exchange_info():
    """
    Gets all information about exchange pairs.
    Weight is 1
    """
    PATH =  '/api/v3/exchangeInfo'
    params = None
    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, params=params)
    if r.status_code == 200:
        # uncomment if I want the raw API response
        #print(json.dumps(r.json(), indent=2))
        data = r.json()
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
        data='API CALL DID NOT WORK'
    return data

binance_info=get_exchange_info()
print(binance_info)
##########################################################################

def get_order_book(symbol,limit=100):
    """
    Default limit is 100 so this is set, although limit is not a required param.
    Valid limits:[5, 10, 20, 50, 100, 500, 1000, 5000]
    Weight is adjusted based on limit
    Limit	                Weight
    5, 10, 20, 50, 100	    1
    500	                    5
    1000	                10
    5000	                50

    Arguments:
        symbol {string} -- This is the symbol pairing to get the order book for.
        limit {int} -- The number of top bids/asks to get on either side of the book.
    """

    PATH = '/api/v1/depth'
    params = {
        'symbol': f'{symbol}',
        'limit': limit
    }

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        order_book=json.dumps(r.json(), indent=2)
        #print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
    return order_book

#order_book_test=get_order_book('BTCUSDT',5)
#print(order_book_test)

##########################################################################

def get_recent_trades(symbol,limit=500):
    """
    Default limit is 500 so this is set, although limit is not a required param.
    Gets up to last 500 recent trades.
    Weight is 1

    Arguments:
        symbol {string} -- trading pair
        limit {int} -- default is 500, max is 1000
    """
    PATH = '/api/v3/trades'
    params = {
        'symbol': f'{symbol}',
        'limit': limit
    }

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        recent_trades=json.dumps(r.json(), indent=2)
        #print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
    return recent_trades

#recent_trades=get_recent_trades('ETHBTC',500)
#print(recent_trades)
##########################################################################

def get_older_trades(symbol, limit=500, **kwargs):
    """
    Default limit is 500 so this is set, although limit is not a required param.
    The other possible argument is fromId
    Gets older trades.
    fromId is the TradeId to fetch from.
    limit is default to 500, max 1000.
    weight is 5

    Arguments:
        symbol {str} -- trading pair
        limit {int} -- results to return
        fromId {int} -- tradeId to fetch from
    """

    PATH = '/api/v3/historicalTrades'
    fromId = kwargs.get('fromId', None)
    params = {
        'symbol': f'{symbol}',
        'limit': limit ,
        'fromId': fromId
    }

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        older_trades=json.dumps(r.json(), indent=2)
        #print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
    return older_trades

#old_trades=get_older_trades('ETHBTC')
#print(old_trades)
##########################################################################

def get_agg_trades(symbol, limit=500, **kwargs):
    """
    Default limit is 500 so this is set, although limit is not a required param.
     fromId, startTime, endTime, are optional kwards
    weight is 1
    Gets aggregate trades.
    fromId is the ID to get aggregate trades from INCLUSIVE.
    limit is default to 500, max 1000.
    startTime and endTime are Timestamps in ms to get aggregate trades from INCLUSIVE.
    If both startTime and endTime are sent, time between startTime and endTime must be less than 1 hour.
    If fromId, startTime, and endTime are not sent, the most recent aggregate trades will be returned.
    Arguments:
        symbol {str} -- trading pair
        limit {int} -- results to return
        fromId {int} -- tradeId to fetch from

    EX response
    {
    "a": 26129,         // Aggregate tradeId
    "p": "0.01633102",  // Price
    "q": "4.70443515",  // Quantity
    "f": 27781,         // First tradeId
    "l": 27781,         // Last tradeId
    "T": 1498793709153, // Timestamp
    "m": true,          // Was the buyer the maker?
    "M": true           // Was the trade the best price match?
    }
    """

    PATH = '/api/v3/aggTrades'
    fromId = kwargs.get('fromId', None)
    startTime = kwargs.get('startTime', None)
    endTime = kwargs.get('endTime', None)

    params = {
        'symbol': f'{symbol}',
        'limit': limit ,
        'fromId': fromId ,
        'startTime': startTime ,
        'endTime': endTime
    }

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        agg_trades=json.dumps(r.json(), indent=2)
        #print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
    return agg_trades
# Not sure what the combos of fromId, startTime, endTime are yet...
#agg_trades=get_agg_trades('ETHBTC')
#print(agg_trades)
##########################################################################

def get_candlesticks(symbol, limit=500, interval='1h', **kwargs):
    """
    get candlesticks
    interval options:
    1m,3m,5m,15m,30m1h,2h,4h,6h,8h,12h,1d,3d,1w,1M
    weight is 1
    If startTime and endTime are not sent, the most recent klines are returned.

    Arguments:
        symbol {[type]} -- [description]
        interval {int} -- [description]
        startTime {[type]} -- [description]
        endTime {[type]} -- [description]
        limit {[type]} -- [description]
    optional args:
    startTime, endTime

    EX response:
    [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore.
    """

    PATH = '/api/v3/klines'
    startTime = kwargs.get('startTime', None)
    endTime = kwargs.get('endTime', None)

    params = {
        'symbol': f'{symbol}',
        'interval': f'{interval}',
        'limit': limit ,
        'startTime': startTime ,
        'endTime': endTime
    }

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        candles=json.dumps(r.json(), indent=2)
        #print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
    return candles

#candle_test=get_candlesticks('ETHBTC',5)
#print(candle_test)
##########################################################################

def get_avg_price(symbol):
    """
    gets the avg price for a given symbol
    """
    PATH = '/api/v3/avgPrice'

    params = {
        'symbol': f'{symbol}'
    }

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        avg_price=json.dumps(r.json(), indent=2)
        #print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
    return avg_price

#avg_pricetest=get_avg_price('ETHBTC')
#print(avg_pricetest)
##########################################################################

def get_24_hr_ticker_price_change(symbol):
    """
    symbol is not required but making it so here.
    Weight: 1 for a single symbol; 40 when the symbol parameter is omitted
    """
    PATH = '/api/v3/ticker/24hr'

    params = {
        'symbol': f'{symbol}'
    }

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        ticker_price=json.dumps(r.json(), indent=2)
        #print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
    return ticker_price

#ticker_test=get_24_hr_ticker_price_change('ETHBTC')
#print(ticker_test)
##########################################################################

def get_latest_price(symbol):
    """
    Gets the latest price for a symbol
    Weight: 1 for a single symbol; 2 when the symbol parameter is omitted
    Use symbol=None to get all prices

    """
    PATH = '/api/v3/ticker/price'
    if symbol==None:
        params=None
    else:
        params = {
            'symbol': f'{symbol}'
        }

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        ticker_price=json.dumps(r.json(), indent=2)
        #print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
    return ticker_price

#latest_ticker_test=get_latest_price('ETHBTC')
#print(latest_ticker_test)
##########################################################################

def get_top_of_book(symbol):
    """
    Gets the top of book best price/qty on the order book for a symbol
    Weight: 1 for a single symbol; 2 when the symbol parameter is omitted
    Use a symbol of None to get all tickers.

    """
    PATH = '/api/v3/ticker/bookTicker'
    if symbol==None:
        params=None
    else:
        params = {
            'symbol': f'{symbol}'
        }

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        top_of_book=json.dumps(r.json(), indent=2)
        #print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
    return top_of_book

#top_of_book_test=get_top_of_book(None)
#print(top_of_book_test)


