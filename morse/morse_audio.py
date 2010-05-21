#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epx@epx.com.br>

import sys, time

class Beeper(object):
	def __init__(self):
		pass

	def play(self, bit):
		print bit
		time.sleep(cfg['duration' + bit])

	def flush(self):
		pass


def configure(sampling_rate, cfg):
	cfg['audio'] = Beeper()
	cfg['compensation'] = 1.0

	if sys.platform == 'darwin':
		try:
			import morse_audio_osxca
			cfg['audio'] = morse_audio_osxca.factory(sampling_rate)
			cfg['wavheader'] = False
			cfg['wavformat'] = 'float'
			cfg['compensation'] = 1
		except ImportError:
			print >> sys.stderr, "CoreAudio plugin not found/not compiled; Using secondary NSAudio plugin"
			import morse_audio_osxna
			cfg['audio'] = morse_audio_osxna.factory(sampling_rate)
			cfg['wavheader'] = True
			cfg['wavformat'] = 'str'
			cfg['compensation'] = 1.42

	elif sys.platform == 'linux2':
		import morse_audio_oss
		cfg['audio'] = morse_audio_oss.factory(sampling_rate)
		cfg['wavheader'] = False
		cfg['wavformat'] = 'str'
