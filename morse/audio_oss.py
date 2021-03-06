#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epxx@epxx.co>

import ossaudiodev

class Beeper(object):
	def open_audio(self):
		if self.impl:
			self.close_audio()
		self.impl = ossaudiodev.open("/dev/dsp", "w")
		self.impl.setparameters(ossaudiodev.AFMT_S16_LE, 1, self.sampling_rate)
		self.impl.nonblock()
		self.playing = False

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

		if len(self.buf) > self.watermark or self.playing:
			# We begin to play something once we have
			# enough data or we had already begun
			if self.impl.obuffree() > 0:
				self.playing = True
				written = self.impl.write(self.buf)
				self.buf = self.buf[written:]
				if not self.buf:
					# underflow, stop for refill
					self.playing = False

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
			self.playing = False

	def final_flush(self):
		self.eol_flush()

def factory(sampling_rate):
	return Beeper(sampling_rate)
