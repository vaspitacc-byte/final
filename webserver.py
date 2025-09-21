from flask import Flask
import threading

def start_webserver():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "OK", 200

    # Run the server in a separate thread so it doesn't block the bot
    thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080))
    thread.daemon = True
    thread.start()