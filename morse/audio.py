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

	def eol_flush(self):
		pass

	def final_flush(self):
		pass

def configure(sampling_rate, cfg):
	cfg['audio'] = Beeper()
	cfg['compensation'] = 1.0

	if sys.platform == 'darwin':
		try:
			from . import audio_coreaudio
			cfg['audio'] = audio_coreaudio.factory()
			# CoreAudio imposes a sampling rate on us
			sampling_rate = cfg['audio'].sampling_rate
			cfg['wavheader'] = False
			cfg['wavformat'] = 'float'
		except ImportError:
			print >> sys.stderr, "CoreAudio plugin not found, using NSAudio"
			from . import audio_nsaudio
			cfg['audio'] = audio_nsaudio.factory(sampling_rate)
			cfg['wavheader'] = True
			cfg['wavformat'] = 'str'
			cfg['compensation'] = 1.15
		except RuntimeError, e:
			print >> sys.stderr, "CoreAudio device could not be configured, using NSAudio"
			print >> sys.stderr, "(Error: %s)" % (" ".join(e.args))
			from . import audio_nsaudio
			cfg['audio'] = audio_nsaudio.factory(sampling_rate)
			cfg['wavheader'] = True
			cfg['wavformat'] = 'str'
			cfg['compensation'] = 1.15

	elif sys.platform == 'linux2':
		from . import audio_oss
		cfg['audio'] = audio_oss.factory(sampling_rate)
		cfg['wavheader'] = False
		cfg['wavformat'] = 'str'

	return sampling_rate
