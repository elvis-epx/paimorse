#!/bin/bash

while true; do
	./twitter_status.py | ./cw -f 800 -v 0.25 -w 15 -s 8
	date
	sleep 600
done
