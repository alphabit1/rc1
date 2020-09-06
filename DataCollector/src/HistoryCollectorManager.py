import collectors.TradeHistoryCollector as THC


class HistoryCollectorManager:
    def __init__(self, db):
        self.collectors = {}
        for exchange in db.getExchanges():
            self.collectors[exchange['key']
                            ] = THC.TradeHistoryCollector(db, exchange)

    def start(self):
        for collector in self.collectors:
            self.collectors[collector].start()
