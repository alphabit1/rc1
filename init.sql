CREATE TABLE exchange (
    id SERIAL PRIMARY KEY,
    name character varying NOT NULL,
    key character varying NOT NULL UNIQUE
);

CREATE TABLE exchange_symbol (
    id SERIAL PRIMARY KEY,
    name character varying NOT NULL,
    key character varying NOT NULL,
    "exchangeId" integer REFERENCES exchange(id),
    live integer DEFAULT 0,
    history integer DEFAULT 0,
    "historyStatus" text
);
CREATE TABLE trade (
    time timestamp with time zone,
    price numeric NOT NULL,
    size numeric NOT NULL,
    side integer NOT NULL,
    exchangeid character varying,
    "symbolId" integer REFERENCES exchange_symbol(id),
    live integer DEFAULT 0,
    CONSTRAINT "PK_trade_time_exchangeid_symbol_id" PRIMARY KEY (time, exchangeid, "symbolId")
);

-- Indices -------------------------------------------------------

CREATE UNIQUE INDEX "PK_exchange_id" ON exchange(id int4_ops);
CREATE UNIQUE INDEX "UQ_exchange_key" ON exchange(key text_ops);
CREATE UNIQUE INDEX "PK_exchange_symbol_id" ON exchange_symbol(id int4_ops);
CREATE UNIQUE INDEX "UQ_trade_time_exchangeid_symbol_id" ON trade(time timestamptz_ops,exchangeid text_ops,"symbolId" int4_ops);
SELECT create_hypertable('trade', 'time', 'symbolId', 10);
CREATE OR REPLACE FUNCTION public.notify_trade_inserted() RETURNS trigger LANGUAGE plpgsql AS $function$ BEGIN PERFORM pg_notify('new_trade_inserted_event', row_to_json(NEW)::text); RETURN NULL; END; $function$;
CREATE TRIGGER updated_test_trigger AFTER INSERT ON trade FOR EACH ROW EXECUTE PROCEDURE notify_trade_inserted();


INSERT INTO "exchange"("id","name","key")
VALUES (1,E'bitmex',E'bitmex');
INSERT INTO "exchange_symbol"("id","name","key","exchangeId","live","history","historyStatus")
VALUES (1,E'xbtusd',E'XBTUSD',1,0,1,E'');