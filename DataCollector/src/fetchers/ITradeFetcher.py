from abc import ABCMeta, abstractmethod


class ITradeFetcher:
    __metaclass__ = ABCMeta

    @classmethod
    def version(self): return "1.0"

    @abstractmethod
    def fetchTrades(self, startDate, symbol): raise NotImplementedError

    @abstractmethod
    def fetchFirstTrade(self, symbol): raise NotImplementedError
