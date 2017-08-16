#!/bin/bash

./twitter_status.py | ./cw -f 800 -v 0.25 -w 20 -s 6
