# webserver.py
from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def start_webserver():
    def run():
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
    
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()