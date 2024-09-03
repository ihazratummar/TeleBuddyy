from flask import Flask, request
from threading import Thread
from telegram import Update



app = Flask(__name__)
@app.route('/')
def index():
    return "Alive"

def run():
    app.run(host='0.0.0.0', port=4000)



def keep_alive():
    t = Thread(target = run)
    t.start()