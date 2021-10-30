# Repl discord.py keep_alive script for UptimeRobot
from flask import Flask
from threading import Thread

print('[INFO] BOT|BOOT: Executing webserver for keep alive purposes...')

app = Flask(__name__)

@app.route('/')
def main():
    return "MCReaper is running!"
# ---------------------------------------------------------------------------
# Not in use
def run():
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)