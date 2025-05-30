import os
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

# Carga precios semanales de los tickers con conversion a tipos nativos
def load_prices(conn, tickers):
    cur = conn.cursor()
    for ticker in tickers:
        data = yf.Ticker(ticker).history(period='1wk')
        for idx, row in data.iterrows():
            date = idx.date()
            # cast a tipos nativos para evitar np.float64
            close = float(row['Close']) if row['Close'] is not None else None
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

# Carga estados financieros trimestrales de los tickers con conversion a tipos nativos
def load_financials(conn, tickers):
    cur = conn.cursor()
    for ticker in tickers:
        tk = yf.Ticker(ticker)
        fin = tk.quarterly_financials
        bs  = tk.quarterly_balance_sheet
        for period in fin.columns:
            ebitda = fin.at['Ebitda', period] if 'Ebitda' in fin.index else None
            equity = bs.at['Total Stockholder Equity', period] if 'Total Stockholder Equity' in bs.index else None
            debt   = bs.at['Long Term Debt', period] if 'Long Term Debt' in bs.index else None
            ebitda_val = float(ebitda) if ebitda is not None else None
            equity_val = float(equity) if equity is not None else None
            debt_val   = float(debt)   if debt   is not None else None
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

# Punto de entrada
if __name__ == '__main__':
    tickers = os.getenv('TICKERS', '').split(',')
    if not tickers or tickers == ['']:
        raise ValueError('Define TICKERS en .env, ej: "AAPL,MSFT,GOOG"')
    conn = get_conn()
    load_prices(conn, tickers)
    load_financials(conn, tickers)
    conn.close()
