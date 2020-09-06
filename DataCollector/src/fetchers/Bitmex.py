import datetime
import requests
import json
from time import sleep
from dateutil.parser import parse
from .ITradeFetcher import ITradeFetcher


class Bitmex(ITradeFetcher):
    name = "bitmex"

    def fetchFirstTrade(self, symbol):
        payload = {
            'count': 1,
            'reverse': 0,
            'symbol': symbol,
            'start': 0,
            'startTime': ''
        }
        r = requests.get('https://www.bitmex.com/api/v1/trade', params=payload)
        if r.status_code == 200:
            return self.parseTrade(json.loads(r.text)[0])
        if r.status_code == 429:
            secondsToWait = int(json.loads(r.text)['error']['message'].replace(
                'Rate limit exceeded, retry in', '').replace('seconds.', '').strip()) * 2
            # print('slow down, wait ' + str(secondsToWait) + 's')
            sleep(secondsToWait)
            return self.getFirstTrade(symbol)
        if r.status_code == 502:
            sleep(1)
            return self.fetchTrades(startDate, symbol)
        print(r.text)
        print(r.status_code)

    def fetchTrades(self, startDate, symbol):

        payload = {
            'count': 1000,
            'reverse': 0,
            'symbol': symbol,
            'start': 0,
            # to be sure we dont skip a trade with the same timestamp we take off 1 microsecond from the startDate
            # TODO: find better solution, 999+ trades with same stamp is problem
            'startTime': startDate - datetime.timedelta(microseconds=1)
        }
        r = requests.get('https://www.bitmex.com/api/v1/trade', params=payload)
        if r.status_code == 200:
            return self.parseTrades(json.loads(r.text))
        if r.status_code == 429:
            secondsToWait = int(json.loads(r.text)['error']['message'].replace(
                'Rate limit exceeded, retry in', '').replace('seconds.', '').strip()) * 2
            # print('slow down, wait ' + str(secondsToWait) + 's')
            sleep(secondsToWait)
            return self.fetchTrades(startDate, symbol)
        if r.status_code == 502:
            sleep(1)
            return self.fetchTrades(startDate, symbol)
        print(r.text)
        print(r.status_code)

    def parseTrades(self, trades):
        result = []
        for trade in trades:
            result.append(self.parseTrade(trade))
        return result

    def parseTrade(self, trade):
        return {
            'time': parse(trade.get('timestamp')),
            'symbolId': trade.get('symbol'),
            'side': 1 if trade['side'] == 'Buy' else 0,
            'price': trade.get('price'),
            'size': trade.get('size'),
            'exchangeid': trade.get('trdMatchID')
        }
