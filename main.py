#!/usr/bin/env python3
# encoding: utf-8

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
  return "UTR"

def run():
  app.run(host="0.0.0.0", port=8000)

def keep_alive():
  server = Thread(target=run)
  server.start()

import subprocess, os, sys

# ---------------------------------------------------------------------------
# Modules (check if modules are installed, will come with a better implementation soon)
try:
    import discord, json, asyncio, random, nekos, pyfiglet, pymongo
except ImportError:
    print(
    'You baka! You forgot to install the required modules in requirements.txt!',
    '\nInstall them with pip install -r requirements.txt'
    )
    exit()
# ---------------------------------------------------------------------------

def start():          
    while True:
        if os.path.isfile('quit.txt'):
            kill = open('quit.txt').read()
            os.remove('quit.txt')
            if kill == 'update':
                exit(15)
            break
        params = [sys.executable, 'mcreaper.py']
        params.extend(sys.argv[1:])
        subprocess.call(params)

if __name__ == '__main__':
    try:
        start()
    except KeyboardInterrupt:
        print('Received KeyboardInterrupt, bye bye!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
