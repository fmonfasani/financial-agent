-- sql/create_tables.sql

-- Tabla de precios históricos
CREATE TABLE IF NOT EXISTS prices (
    date       DATE    NOT NULL,
    ticker     TEXT    NOT NULL,
    close      NUMERIC,
    volume     BIGINT,
    PRIMARY KEY (date, ticker)
);

-- Tabla de estados financieros básicos
CREATE TABLE IF NOT EXISTS financials (
    ticker      TEXT    NOT NULL,
    period_end  DATE    NOT NULL,
    ebitda      NUMERIC,
    equity      NUMERIC,
    debt        NUMERIC,
    PRIMARY KEY (ticker, period_end)
);
