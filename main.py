import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

from bot import get_reply, chat_sessions
from commands import is_command, handle_command

load_dotenv()

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


# ── Webhook verification (Meta calls this once when you set up the webhook) ──
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified!")
        return challenge, 200

    print("Webhook verification failed.")
    return "Forbidden", 403


# ── Incoming messages ────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health_check():
    return "Sparky is alive! 🚀", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # Ignore status updates (delivered, read, etc.)
        if "messages" not in value:
            return "ok", 200

        message = value["messages"][0]
        sender = message["from"]
        msg_type = message.get("type")

        # Only handle text messages for now
        if msg_type != "text":
            send_whatsapp_message(sender, "⚠️ Sorry, I currently only support text messages!")
            return "ok", 200

        incoming_msg = message["text"]["body"].strip()
        print(f"Message from {sender}: {incoming_msg}")

        # Route to command handler or AI
        if is_command(incoming_msg):
            reply = handle_command(incoming_msg, sender, chat_sessions)
        else:
            reply = get_reply(sender, incoming_msg)

        send_whatsapp_message(sender, reply)

    except (KeyError, IndexError) as e:
        print(f"Error parsing incoming message: {e}")

    return "ok", 200


# ── Send a WhatsApp message via Meta API ────────────────────────────────────
def send_whatsapp_message(to: str, text: str):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"Failed to send message: {response.status_code} — {response.text}")
    else:
        print(f"Message sent to {to}")


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)