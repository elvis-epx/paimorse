#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epx@epx.com.br>

import ossaudiodev

class OSSBeeper(Beeper):
	def open_audio(self):
		if self.impl:
			self.close_audio()
		self.impl = ossaudiodev.open("/dev/dsp", "w")
		self.impl.setparameters(ossaudiodev.AFMT_S16_LE, 1, self.sampling_rate)
		self.impl.nonblock()

	def close_audio(self):
		if self.impl:
			self.impl.close()
		self.impl = None

	def __init__(self, sampling_rate):
		self.impl = None
		self.buf = ""
		self.sampling_rate = sampling_rate
		self.open_audio()
		self.watermark = self.impl.bufsize()

	def play(self, sample):
		if not self.impl:
			self.open_audio()

		self.buf += sample

		if len(self.buf) > self.watermark:
			# Let's begin to play something
			if self.impl.obuffree() > 0:
				written = self.impl.write(self.buf)
				self.buf = self.buf[written:]

		if len(self.buf) > 10 * self.watermark:
			# Does not let buffer grow too long
			length = 5 * self.watermark
			data = self.buf[:length]
			self.buf = self.buf[length:]
			self.impl.writeall(data)

	def eol_flush(self):
		if self.buf:
			# Make sure buffer goes out
			data = self.buf
			self.buf = ""
			self.impl.writeall(data)

	def final_flush(self):
		self.eol_flush()

def factory(sampling_rate):
	return OSSBeeper(sampling_rate)

# FIXME after begins to play, should not stop until buffer is empty
# FIXME put in its own thread
# FIXME implement eol_flush
