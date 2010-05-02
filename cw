#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epx@epx.com.br>

from morse import *
import sys
from StringIO import StringIO
import getopt

def usage(err=""):
	if err:
		print err
		print "Call '%s --help' or '%s -h' for instructions" % \
			 (sys.argv[0], sys.argv[0])
		sys.exit(1)
	print "Usage: %s [ -f freq (Hz) ] [ -v volume (0.0-1.0) ] " \
		"[ -w speed (in wpm) ] [ -d dash_length (in dots) ] " \
		"[ -b interbit_spacing (in dots) ] " \
		"[ -s interletter_spacing (in dots) ] word1 word2 ..." % sys.argv[0]
	print
	print "Examples: "
	print
	print "%s -f 440 -v 0.5 -w 15 -d 3 -b 0.5 -s 3 bla bla" % sys.argv[0]
	print "cat msg.txt | %s -w 20" % sys.argv[0]
	print "%s SOS SOS SOS" % sys.argv[0]
	print
	print "Speed (-w) is specified in words per minute. 20 WPM means"
	print "a dot of 60ms (1200 divided by 20, the 'Paris' standard)."
	print "Dash length, as well as interbit and inter-letter spacings"
	print "are expressed relative to the dot size (-w 20 -d 3 means a"
	print "dash of 180ms, three times a 60ms dot."
	print "Interbit spacing is between dashes/dots of a single letter."
	print
	print "The defaults are: 800Hz, volume 0.25, 12 words per minute,"
	print "dashes 3x dot, interbit spacing is 0.6x dot, interletter"
	print "spacing is 2.5x a dot. Inter-word spacing is fixed as twice"
	print "the interletter silence."
	sys.exit(1)

def interpret_args(args):
	freq = 0
	volume = 0
	wpm = 0
	dash = 0
	interbit = 0
	intersymbol = 0
	try:
		opts, args = getopt.gnu_getopt(sys.argv[1:],
						"f:v:w:d:b:s:h",
						["help"])
	except getopt.GetoptError:
		usage("Invalid or unexpected parameter")

	for option, value in opts:
		if option == "-h" or option == "--help":
			usage("")
		try:
			value = float(value)
		except ValueError:
			usage("%s needs a numeric argument (can be decimal)" % option)
		if value <= 0:
			usage("%s argument must be greater than zero" % option)
		if option == "-f":
			if value > 11000:
				usage("Frequency must be smaller than 11000")
			freq = value
		if option == "-v":
			if value < 0.0001 or value > 1.0:
				usage("Volume must be between 0.0001 and 1.0")
			volume = value
		if option == "-w":
			if value < 1 or value > 2000:
				usage("Speed in words per minue must be between 1 and 2000")
			wpm = value
		if option == "-d":
			if value < 1 or value > 10:
				usage("Dash size must be between 1 and 10 dots")
			dash = value
		if option == "-b":
			if value < 0 or value > 10:
				usage("Interbit silence must be between 0 and 10 dots")
			interbit = value
		if option == "-s":
			if value < 0 or value > 10:
				usage("Interletter silence must be between 0 and 10 dots")
			intersymbol = value
	
	if opts:
		config(freq, volume, wpm, dash, interbit, intersymbol)

	return opts, args

if len(sys.argv) > 1:
	opts, args = interpret_args(sys.argv[1])
	fd = StringIO(" ".join(args))
else:
	fd = sys.stdin

while True:
	text = fd.readline().decode('utf-8')
	if not text:
		break
	fixed_text, bits = encode_morse(text)
	print fixed_text
	print bits
	play_morse_bits(bits)
