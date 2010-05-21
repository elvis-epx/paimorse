#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epx@epx.com.br>

import thread
import coreaudio
import time

CHUNK = 512 # demanded by coreaudio module

# TODO define this as a multiple of coreaudio buffer
HALFBUF = 50000
MAXBUF = HALFBUF * 2

class CoreAudioBeeper(object):
	def callback(self):
		buf = None

		if not self.buf:
			self.close_audio()
		elif len(self.buf) < CHUNK:
			buf = self.buf
			# Fill with silence to have len == CHUNK
			buf.extend([0.0 for i in xrange(0, CHUNK - len(buf))])
			self.buf = []
			self.close_audio()
		else:
			buf = self.buf[:CHUNK]
			self.buf = self.buf[CHUNK:]

		return buf

	def audio_closed(self):
		pass

	def open_audio(self):
		if not self.active:
			coreaudio.installAudioCallback(self)
		self.active = True

	def close_audio(self):
		if self.active:
			coreaudio.stopAudio(self)
		self.active = False
		self.buf = []

	def __init__(self, sampling_rate):
		self.active = False
		self.buf = []
		self.sampling_rate = sampling_rate
		CHUNK = 512

	def play(self, sample):
		self.buf.extend(sample)

		if len(self.buf) > CHUNK:
			# Let's begin to play something
			self.open_audio()

		if len(self.buf) > MAXBUF:
			# Does not let buffer grow too long
			self._flush(False)

	def _flush(self, complete):
		# Does actual buffer flushing
		while (complete and self.buf) or (not complete and len(self.buf) > HALFBUF):
			print "buffer %d %s, waiting" % (len(self.buf), complete)
			time.sleep(0.1)
			# FIXME wait buffer empty in a more proper way

	def flush(self):
		# play whatever we have
		if self.buf and not self.active:
			self.active_audio()
		self._flush(True)

# Have to initialize the threading mechanisms in order for PyGIL_Ensure to work
thread.start_new_thread(lambda: None, ())


def factory(sampling_rate):
	return CoreAudioBeeper(sampling_rate)

