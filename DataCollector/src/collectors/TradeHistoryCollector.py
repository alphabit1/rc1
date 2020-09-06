import os
import datetime
import threading
import importlib
from time import sleep


from fetchers.Bitmex import Bitmex


class TradeHistoryCollector (threading.Thread):
    collecting = True
    timeDiff = 3

    def __init__(self, db, exchange):
        threading.Thread.__init__(self)
        self.db = db
        self.exchange = exchange
        module = importlib.import_module(
            'fetchers.' + exchange['key'].capitalize())
        fetcher = getattr(module, exchange['key'].capitalize())
        self.fetcher = fetcher()

    def run(self):
        while self.collecting:
            symbols = self.db.getHistorySymbols(self.exchange)
            for symbol in symbols:
                self.status(symbol, 'cue')

            for symbol in symbols:
                self.collectHistory(symbol)

            for symbol in self.db.getHistorySymbols(self.exchange):
                self.status(symbol, 'sleeping')

            sleep(self.timeDiff)

    def collectHistory(self, symbol):
        firstTrade = self.fetcher.fetchFirstTrade(symbol['key'])
        self.db.storeTrades([firstTrade], symbol['id'])
        while self.isNotFinished(symbol):
            trades = self.fetcher.fetchTrades(
                self.db.getLastTrade(symbol)['time'], symbol['key'])
            self.db.storeTrades(trades, symbol['id'])
            self.status(symbol, 'collecting')
        self.status(symbol, 'finished')

    def isNotFinished(self, symbol):
        return (datetime.datetime.now().timestamp() -
                self.db.getLastTrade(symbol)['time'].timestamp() >
                self.timeDiff) and (self.db.getSymbolHistory(symbol))

    def status(self, symbol, status):
        statusStr = status + ' ' + \
            str(self.db.getFirstTrade(symbol)['time']) + ' - ' + \
            str(self.db.getLastTrade(symbol)['time'])
        # if os.environ['DEBUG']:
        #     print('TradeHistoryCollector ' +
        #           self.exchange['key']+':' + symbol['key'] + ' ' + statusStr)
        self.db.setSymbolHistoryStatus(symbol, statusStr)
