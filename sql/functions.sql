import os
import math
import yfinance as yf
import psycopg2
from datetime import datetime
import urllib.parse as urlparse

# Conexión a la BD usando DATABASE_URL
def get_conn():
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    return psycopg2.connect(
        dbname=url.path.lstrip('/'),
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

# Convertir valores pandas/numpy a tipos nativos, tratando NaN como None
def to_native(val):
    if val is None:
        return None
    try:
        f = float(val)
        if math.isnan(f):
            return None
        return f
    except:
        return None

# Carga precios semanales de los tickers con conversión a tipos nativos
def load_prices(conn, tickers):
    cur = conn.cursor()
    for ticker in tickers:
        data = yf.Ticker(ticker).history(period='1wk')
        for idx, row in data.iterrows():
            date = idx.date()
            close = to_native(row['Close'])
            volume = int(row['Volume']) if row['Volume'] is not None else None
            cur.execute(
                '''
                INSERT INTO prices (date, ticker, close, volume)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (date, ticker)
                DO UPDATE SET close = EXCLUDED.close, volume = EXCLUDED.volume;
                ''',
                (date, ticker, close, volume)
            )
    conn.commit()
    cur.close()

# Carga estados financieros trimestrales de los tickers con conversión a tipos nativos
def load_financials(conn, tickers):
    cur = conn.cursor()

    # Claves exactas de yfinance y fallback keys
    EBITDA_KEYS = ['EBITDA', 'Normalized EBITDA']
    EQUITY_KEYS = ['Stockholders Equity', 'Common Stock Equity']
    DEBT_KEYS   = ['Total Debt', 'Net Debt']

    for ticker in tickers:
        tk = yf.Ticker(ticker)
        fin = tk.quarterly_financials
        bs  = tk.quarterly_balance_sheet
        for period in fin.columns:
            # Obtención de ebitda con fallback
            raw_ebitda = None
            for key in EBITDA_KEYS:
                if key in fin.index:
                    raw_ebitda = fin.at[key, period]
                    break

            # Obtención de equity con fallback
            raw_equity = None
            for key in EQUITY_KEYS:
                if key in bs.index:
                    raw_equity = bs.at[key, period]
                    break

            # Obtención de debt con fallback
            raw_debt = None
            for key in DEBT_KEYS:
                if key in bs.index:
                    raw_debt = bs.at[key, period]
                    break

            ebitda_val = to_native(raw_ebitda)
            equity_val = to_native(raw_equity)
            debt_val   = to_native(raw_debt)

            cur.execute(
                '''
                INSERT INTO financials (ticker, period_end, ebitda, equity, debt)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (ticker, period_end)
                DO UPDATE SET ebitda=EXCLUDED.ebitda, equity=EXCLUDED.equity, debt=EXCLUDED.debt;
                ''',
                (ticker, period.date(), ebitda_val, equity_val, debt_val)
            )
    conn.commit()
    cur.close()
