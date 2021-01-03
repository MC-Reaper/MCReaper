#!/usr/bin/env python3
# encoding: utf-8

import subprocess, os, sys

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
