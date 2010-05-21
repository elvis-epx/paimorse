#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epx@epx.com.br>

import thread
import coreaudio
import time

CHUNK = 512 # demanded by coreaudio module

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

		print "Tocando buffer de comprimento", len(buf)
		return buf

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
			self.active_audio()

		if len(self.buf) > 10 * CHUNK:
			# Does not let buffer grow too long
			# FIXME wait for 5 * drain to go out
			pass

	def wait(self):
		# play whatever we have
		if self.buf and not self.active:
			self.active_audio()
		while self.buf:
			print "buffer not empty, waiting"
			time.sleep(1)
			# FIXME wait buffer empty in a more proper way
		# FIXME close + immediate open?


# Have to initialize the threading mechanisms in order for PyGIL_Ensure to work
thread.start_new_thread(lambda: None, ())


def factory(sampling_rate):
	return CoreAudioBeeper(sampling_rate)

