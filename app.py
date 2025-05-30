import os

from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

# tokens desde .env
SLACK_BOT_TOKEN     = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_APP_TOKEN     = os.environ.get("SLACK_APP_TOKEN")  
PORT                = int(os.environ.get("PORT", 3000))


bolt_app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    process_before_response=True,  #
)

@bolt_app.command(os.environ.get("SLASH_COMMAND", "/ratio"))
def handle_ratio(ack, respond, command):
    ack()
    
    respond(f"pong!")

if SLACK_APP_TOKEN:
    
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    handler = SocketModeHandler(bolt_app, SLACK_APP_TOKEN)
    if __name__ == "__main__":
        handler.start()
else:
    
    flask_app = Flask(__name__)
    handler = SlackRequestHandler(bolt_app)

    @flask_app.route("/", methods=["GET"])
    def healthcheck():
        return jsonify({"status": "ok"}), 200

    @flask_app.route("/slack/events", methods=["POST"])
    def slack_events():
        return handler.handle(request)

    if __name__ == "__main__":
        flask_app.run(host="0.0.0.0", port=PORT)
