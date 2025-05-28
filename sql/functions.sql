-- PER promedio entre fechas
CREATE OR REPLACE FUNCTION per_avg(
    ticker_symbol TEXT,
    start_date DATE,
    end_date DATE
) RETURNS NUMERIC LANGUAGE plpgsql AS $$
DECLARE
    avg_val NUMERIC;
BEGIN
    SELECT AVG(p.close / NULLIF((f.ebitda / f.equity),0)) INTO avg_val
    FROM prices p
    JOIN financials f ON p.ticker = f.ticker
    WHERE p.ticker = ticker_symbol
      AND p.date BETWEEN start_date AND end_date;
    RETURN avg_val;
END;
$$;

-- P/B promedio
CREATE OR REPLACE FUNCTION pb_avg(
    ticker_symbol TEXT,
    start_date DATE,
    end_date DATE
) RETURNS NUMERIC LANGUAGE plpgsql AS $$
DECLARE
    avg_val NUMERIC;
BEGIN
    SELECT AVG(p.close / NULLIF(f.equity,0)) INTO avg_val
    FROM prices p
    JOIN financials f ON p.ticker = f.ticker
    WHERE p.ticker = ticker_symbol
      AND p.date BETWEEN start_date AND end_date;
    RETURN avg_val;
END;
$$;

-- ROE promedio (%)
CREATE OR REPLACE FUNCTION roe_avg(
    ticker_symbol TEXT,
    start_date DATE,
    end_date DATE
) RETURNS NUMERIC LANGUAGE plpgsql AS $$
DECLARE
    avg_val NUMERIC;
BEGIN
    SELECT AVG(NULLIF((f.ebitda / f.equity) * 100,0)) INTO avg_val
    FROM financials f
    WHERE f.ticker = ticker_symbol
      AND f.period_end BETWEEN start_date AND end_date;
    RETURN avg_val;
END;
$$;

-- Deuda/EBITDA promedio
CREATE OR REPLACE FUNCTION debt_ebitda_avg(
    ticker_symbol TEXT,
    start_date DATE,
    end_date DATE
) RETURNS NUMERIC LANGUAGE plpgsql AS $$
DECLARE
    avg_val NUMERIC;
BEGIN
    SELECT AVG(NULLIF(f.debt / NULLIF(f.ebitda,0),0)) INTO avg_val
    FROM financials f
    WHERE f.ticker = ticker_symbol
      AND f.period_end BETWEEN start_date AND end_date;
    RETURN avg_val;
END;
$$;
