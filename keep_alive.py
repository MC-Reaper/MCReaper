# Repl discord.py keep_alive script for UptimeRobot
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
    return "MCReaper is running!"
# ---------------------------------------------------------------------------
def run():
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)

def keep_alive():
    server = Thread(target=run)
    server.start()