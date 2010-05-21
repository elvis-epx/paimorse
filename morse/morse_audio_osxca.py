#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epx@epx.com.br>

import thread
from threading import RLock, Event
import coreaudio
import time

CHUNK = 512 # demanded by coreaudio module

# TODO define this as a multiple of coreaudio buffer
HALFBUF = 50000
MAXBUF = HALFBUF * 2


class CoreAudioBeeper(object):

	def callback(self):
		# Called in another thread's context
		chunk = None
		last_chunk = False

		self.lock.acquire()

		if not self.buf:
			self.close_audio()
		elif len(self.buf) < CHUNK:
			chunk = self.buf
			# Fill with silence to have len == CHUNK
			chunk.extend([0.0 for i in xrange(0, CHUNK - len(chunk))])
			self.buf = []
			last_chunk = True
		else:
			chunk = self.buf[:CHUNK]
			self.buf = self.buf[CHUNK:]

		self.lock.release()

		if last_chunk:
			self.close_audio()

		self.event.set()

		return chunk

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

	def __init__(self, sampling_rate):
		self.active = False
		self.buf = []
		self.sampling_rate = sampling_rate
		self.event = Event()
		self.lock = RLock()

	def play(self, sample):
		self.lock.acquire()
		self.buf.extend(sample)
		l = len(self.buf)
		self.lock.release()

		if l > CHUNK:
			# Let's begin to play something
			self.open_audio()

		if l > MAXBUF:
			# Does not let buffer grow too long
			self._flush(False)

	def _flush(self, complete):
		# Blocks until buffer is half or fully emptied
		self.lock.acquire()
		l = len(self.buf)
		self.lock.release()
		while (complete and l > 0) or (not complete and l > HALFBUF):
			self.event.wait()
			self.event.clear()
			self.lock.acquire()
			l = len(self.buf)
			self.lock.release()

	def eol_flush(self):
		# put to play whatever we have
		self.lock.acquire()
		notempty = not not self.buf
		self.lock.release()

		if notempty and not self.active:
			self.active_audio()

	def final_flush(self):
		self.eol_flush()
		self._flush(True)

# Have to initialize the threading mechanisms in order for PyGIL_Ensure to work
thread.start_new_thread(lambda: None, ())


def factory(sampling_rate):
	return CoreAudioBeeper(sampling_rate)

# FIXME protect callback() with mutex
