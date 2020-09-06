import os
import psycopg2
import datetime
from psycopg2 import sql
from psycopg2.extras import execute_values


class Db:
    select = "SELECT * FROM {}"
    selectBy = "SELECT * FROM {} WHERE {} = %s "
    selectByAnd = "SELECT * FROM {} WHERE {} = %s AND {} = %s"
    selectFirst = "SELECT * FROM trade WHERE \"symbolId\" = %s AND live = 0 ORDER BY time ASC LIMIT 1"
    selectLast = "SELECT * FROM trade WHERE \"symbolId\" = %s AND live = 0 ORDER BY time DESC LIMIT 1"
    updateSingle = "UPDATE {} SET {} = %s WHERE {} = %s"

    def __init__(self):
        self.connection = psycopg2.connect(
            database=os.environ['DB_DB'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'])

    def getExchanges(self):
        cur = self.connection.cursor()
        cur.execute(sql.SQL(self.select).format(
            sql.Identifier('exchange')))
        rows = cur.fetchall()
        cur.close()
        res = []
        for row in rows:
            res.append({
                'id': row[0],
                'name': row[1],
                'key': row[2],
            })
        return res

    def setSymbolHistoryStatus(self, symbol, status):
        cur = self.connection.cursor()
        query = sql.SQL(self.updateSingle).format(sql.Identifier(
            'exchange_symbol'), sql.Identifier('historyStatus'), sql.Identifier('id'))
        cur.execute(query, (status, symbol['id']))
        cur.close()
        self.connection.commit()

    def getSymbolHistory(self, symbol):
        cur = self.connection.cursor()
        query = sql.SQL(self.selectBy).format(sql.Identifier(
            'exchange_symbol'), sql.Identifier('id'))
        cur.execute(query, (symbol['id'],))
        row = cur.fetchone()
        return row[5]

    def getHistorySymbols(self, exchange):
        cur = self.connection.cursor()
        query = sql.SQL(self.selectByAnd).format(
            sql.Identifier('exchange_symbol'), sql.Identifier('exchangeId'), sql.Identifier('history'))
        cur.execute(query, (exchange['id'], 1))
        rows = cur.fetchall()
        cur.close()
        res = []
        for row in rows:
            res.append({
                'id': row[0],
                'name': row[1],
                'key': row[2],
                'exchangeId': row[3]
            })
        return res

    def getSymbols(self, exchange):
        cur = self.connection.cursor()
        query = sql.SQL(self.selectBy).format(
            sql.Identifier('exchange_symbol'), sql.Identifier('exchangeId'))
        cur.execute(query, (exchange['id'],))
        rows = cur.fetchall()
        cur.close()
        res = []
        for row in rows:
            res.append({
                'id': row[0],
                'name': row[1],
                'key': row[2],
                'exchangeId': row[3]
            })
        return res

    def getExchange(self, key):
        query = sql.SQL(self.selectBy).format(
            sql.Identifier('exchange'), sql.Identifier('key'))
        cur = self.connection.cursor()
        cur.execute(query, (key.lower(),))
        row = cur.fetchone()
        cur.close()
        return {
            'id': row[0],
            'name': row[1],
            'key': row[2],
        }

    def getSymbol(self, exchange, symbolKey):
        query = sql.SQL(self.selectByAnd).format(
            sql.Identifier('exchange_symbol'), sql.Identifier('exchangeId'), sql.Identifier('key'))
        cur = self.connection.cursor()
        cur.execute(query, (exchange['id'], symbolKey))
        row = cur.fetchone()
        cur.close()
        return {
            'id': row[0],
            'name': row[1],
            'key': row[2],
        }

    def getFirstTrade(self, symbol):
        cur = self.connection.cursor()
        cur.execute(self.selectFirst, (symbol['id'],))
        return self.row2trade(cur.fetchone())

    def getLastTrade(self, symbol):
        cur = self.connection.cursor()
        cur.execute(self.selectLast, (symbol['id'],))
        return self.row2trade(cur.fetchone())

    def getSymbols(self, exchange):
        cur = self.connection.cursor()
        query = sql.SQL(self.selectBy).format(
            sql.Identifier('exchange_symbol'), sql.Identifier('exchangeId'))
        cur.execute(query, (exchange['id'],))
        rows = cur.fetchall()
        cur.close()
        res = []
        for row in rows:
            res.append({
                'id': row[0],
                'name': row[1],
                'key': row[2],
                'exchangeId': row[3]
            })
        return res

    def storeTrades(self, trades, symbolId):
        cur = self.connection.cursor()
        query = "INSERT INTO trade (time, price, size, side, exchangeid, \"symbolId\") VALUES %s ON CONFLICT (time, exchangeid, \"symbolId\") DO UPDATE SET live = 0"
        tradeTupleList = []
        for trade in trades:
            tradeTupleList.append(tuple((trade['time'], trade['price'], trade['size'],
                                         trade['side'], trade['exchangeid'], int(symbolId))))
        execute_values(cur, query, tradeTupleList)
        cur.close()
        self.connection.commit()

    def row2trade(self, row):
        if row == None:
            # return {"time": datetime.datetime(2018, 8, 4)}
            # return {"time": datetime.datetime(2015, 10, 2)}
            return {"time": datetime.datetime.now()}
        return {
            "time": row[0],
            "price": row[1],
            "size": row[2],
            "side": row[3],
            "exchangeid": row[4],
            "symbolId": row[5]
        }
