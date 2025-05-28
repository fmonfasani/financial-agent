import os
from slack_bolt import App
import psycopg2
from datetime import datetime, timedelta

# Configuración desde .env
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLASH_COMMAND   = os.environ.get('SLASH_COMMAND', '/ratio')
TARGET_CHANNEL  = os.environ.get('TARGET_CHANNEL', '#finanzas')

app = App(token=SLACK_BOT_TOKEN)

# Helper de DB

def query_ratio(func, ticker, start, end):
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute(f"SELECT {func}(%s,%s,%s)", (ticker, start, end))
    result = cur.fetchone()[0]
    conn.close()
    return result

@app.command(SLASH_COMMAND)
def handle_ratio(ack, respond, command):
    ack()
    text = command['text']  # "AAPL PER 6m"
    try:
        ticker, ratio, period = text.split()
        end = datetime.utcnow().date()
        months = int(period[:-1]) if period.endswith('m') else int(period)
        start = end - timedelta(days=months * 30)
        func = ratio.lower() + '_avg'
        result = query_ratio(func, ticker, start, end)
        respond(f"*{ratio}* de {ticker} entre {start} y {end}: `{result:.2f}`", channel=TARGET_CHANNEL)
    except Exception as e:
        respond(f"Error procesando tu petición: {e}")

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))