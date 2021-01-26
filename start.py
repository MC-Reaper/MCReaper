#!/usr/bin/env python3
# encoding: utf-8

import subprocess, os, sys

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
