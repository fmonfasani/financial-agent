# app.py
import os
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from slack_bolt import App as BoltApp
from slack_bolt.adapter.flask import SlackRequestHandler
import psycopg2

# --- Configuración desde .env ----------------------
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']
SLASH_COMMAND   = os.environ.get('SLASH_COMMAND', '/ratio')
TARGET_CHANNEL  = os.environ.get('TARGET_CHANNEL', '#finanzas')
DATABASE_URL    = os.environ['DATABASE_URL']
# ---------------------------------------------------

# Crea la app de Bolt
bolt_app = BoltApp(
    token=SLACK_BOT_TOKEN,
    app_token=SLACK_APP_TOKEN,
    process_before_response=True
)

# Función helper para consultar la DB
def query_ratio(func_name, ticker, start_date, end_date):
    conn = psycopg2.connect(DATABASE_URL)
    cur  = conn.cursor()
    cur.execute(f"SELECT {func_name}(%s, %s, %s);",
                (ticker, start_date, end_date))
    val = cur.fetchone()[0]
    cur.close()
    conn.close()
    return val

# Define el comando Slack
@bolt_app.command(SLASH_COMMAND)
def handle_ratio(ack, respond, command):
    ack()
    try:
        ticker, ratio, period = command['text'].split()
        end   = datetime.utcnow().date()
        months = int(period[:-1]) if period.endswith('m') else int(period)
        start = end - timedelta(days=months * 30)
        func = ratio.lower() + '_avg'
        result = query_ratio(func, ticker, start, end)
        respond(
            f"*{ratio}* de {ticker} desde {start} hasta {end}: `{result:.2f}`",
            channel=TARGET_CHANNEL
        )
    except Exception as e:
        respond(f"❌ Error: {e}", channel=TARGET_CHANNEL)

# Monta Flask y el handler de Bolt
flask_app = Flask(__name__)
handler   = SlackRequestHandler(bolt_app)

@flask_app.route("/")
def healthcheck():
    return jsonify({"status":"ok"}), 200

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    flask_app.run(host="0.0.0.0", port=port)
