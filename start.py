#!/usr/bin/env python3
# encoding: utf-8

import subprocess, os, sys

# For heroku only
# ---------------------------------------------------------------------------
# Modules (check if modules are installed, will come with a better implementation soon)
try:
    import discord, json, asyncio, random, nekos, pyfiglet, pymongo, flask
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
        params = [sys.executable, 'main.py']
        params.extend(sys.argv[1:])

        params2 = [sys.executable, 'keep_alive.py']
        params2.extend(sys.argv[1:])

        subprocess.call(params)
        subprocess.call(params2)

if __name__ == '__main__':
    try:
        start()
    except KeyboardInterrupt:
        print('Received KeyboardInterrupt, bye bye!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
