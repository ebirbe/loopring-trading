--
-- File generated with SQLiteStudio v3.2.1 on mar. may. 19 13:39:39 2020
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: candlestick_1hr
DROP TABLE IF EXISTS candlestick_1hr;
CREATE TABLE candlestick_1hr (time DATETIME NOT NULL UNIQUE PRIMARY KEY DESC, txs INTEGER NOT NULL DEFAULT 0, open REAL NOT NULL, close REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL, volume_base REAL, volume_quote REAL) WITHOUT ROWID;

-- Table: candlestick_1min
DROP TABLE IF EXISTS candlestick_1min;
CREATE TABLE candlestick_1min (time DATETIME NOT NULL UNIQUE PRIMARY KEY DESC, txs INTEGER NOT NULL DEFAULT 0, open REAL NOT NULL, close REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL, volume_base REAL, volume_quote REAL);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
