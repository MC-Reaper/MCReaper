#!/bin/bash
pip install -U -r requirements.txt &
wait
python keep_alive.py &
python start.py