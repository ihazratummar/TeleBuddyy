from flask import Flask, request
from threading import Thread
from telegram import Update


def keep_bot(bot):
    return bot




app = Flask(__name__)
@app.route('/')
def index():
    return "Alive"

def run():
    app.run(host='0.0.0.0', port=4000)


@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), keep_bot.app.bot)
    keep_bot.app.process_update(update)
    return 'ok'


def keep_alive():
    t = Thread(target = run)
    t.start()