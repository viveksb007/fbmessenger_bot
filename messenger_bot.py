from flask import Flask, request
import json
import requests
from Credentials import *
import os
from chatterbotapi import ChatterBotFactory, ChatterBotType

app = Flask(__name__)

factory = ChatterBotFactory()
bot1 = factory.create(ChatterBotType.PANDORABOTS, MyPandoraBotId)
bot1session = bot1.create_session()


@app.route('/', methods=['GET'])
def handle_verification():
    if request.args.get('hub.verify_token', '') == VERIFY_TOKEN:
        return request.args.get('hub.challenge', '')
    else:
        return 'Error, wrong validation token'


@app.route('/', methods=['POST'])
def handle_messages():
    payload = request.get_data()
    for sender, message in messaging_events(payload):
        msg = bot1session.think(message)
        if len(msg) > 320:
            for j in range(0, (len(msg) / 320), 1):
                if (j + 1) * 320 <= len(msg):
                    send_message(PAGE_ACCESS_TOKEN, sender, msg[j * 320:(j + 1) * 320])
                else:
                    send_message(PAGE_ACCESS_TOKEN, sender, msg[j * 320:])
        else:
            send_message(PAGE_ACCESS_TOKEN, sender, msg)
    return 'ok'


def messaging_events(payload):
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        if "message" in event and "text" in event["message"]:
            yield event["sender"]["id"], event["message"]["text"].encode('utf-8')
        else:
            yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params={"access_token": token},
                      data=json.dumps({
                          "recipient": {"id": recipient},
                          "message": {"text": text}
                      }),
                      headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print r.text


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
