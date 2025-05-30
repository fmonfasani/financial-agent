#!/usr/bin/env python3
import os
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
import psycopg2


DATABASE_URL      = os.environ["DATABASE_URL"]
SLACK_BOT_TOKEN   = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_TOKEN   = os.environ["SLACK_BOT_TOKEN"]
SLASH_COMMAND     = os.environ.get("SLASH_COMMAND", "/ratio")
TARGET_CHANNEL    = os.environ.get("TARGET_CHANNEL", "#finanzas")
DATABASE_URL      = os.environ["DATABASE_URL"]
PORT              = int(os.environ.get("PORT", 3000))

# 2) Crea tu Bolt App
bolt_app = App(
    token=SLACK_BOT_TOKEN,
    process_before_response=True,   # para que Bolt devuelva ack rápidamente
)

# 3) Helper para consultar la BD
def query_ratio(func_name: str, ticker: str, start: datetime.date, end: datetime.date):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(f"SELECT {func_name}(%s, %s, %s);", (ticker, start, end))
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result

# 4) Slash command handler
@bolt_app.command(SLASH_COMMAND)
def handle_ratio(ack, respond, command):
    ack()
    text = command["text"].strip()        # ej. "AAPL PER 6m"
    try:
        ticker, ratio, period = text.split()
        end = datetime.utcnow().date()
        # interpretamos “6m” como 6 meses (aprox 6*30 días)
        if period.endswith("m"):
            months = int(period[:-1])
            start = end - timedelta(days=months * 30)
        else:
            days = int(period)
            start = end - timedelta(days=days)

        func = ratio.lower() + "_avg"     # per_avg, roe_avg, ...
        value = query_ratio(func, ticker, start, end)
        if value is None:
            respond(f"No hay datos para `{ratio}` de `{ticker}` en este periodo.", channel=TARGET_CHANNEL)
        else:
            respond(
                f"*{ratio.upper()}* de *{ticker}* de `{start}` a `{end}`: `{value:.2f}`",
                channel=TARGET_CHANNEL
            )
    except Exception as e:
        respond(f":warning: Error procesando tu petición: `{e}`", channel=TARGET_CHANNEL)

# 5) Monta Bolt dentro de Flask
flask_app = Flask(__name__)
handler = SlackRequestHandler(bolt_app)

@flask_app.route("/", methods=["GET"])
def healthcheck():
    return jsonify({"status": "ok"}), 200

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# 6) Arranque
if __name__ == "__main__":
    # Asegúrate de que el puerto 3000 está abierto en Codespaces
    flask_app.run(host="0.0.0.0", port=PORT)
