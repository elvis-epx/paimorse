#!/usr/bin/env python

import thread
import coreaudio # http://wiki.python.org/moin/MacPython/CoreAudio
import time
import math

# Sends a silence sound every 10 seconds, just to keep audio board lit

class Ctrl(object):
	def callback(self):
		if self.counter:
			coreaudio.stopAudio(self)
		self.counter += 1
		return self.silence

	def __init__(self):
		self.audio_id, sampling_rate, chunksize = coreaudio.initAudio()
		self.silence = [0.0 for i in range(0, chunksize)]

	def ping(self):
		self.counter = 0
		coreaudio.installAudioCallback(self.audio_id, self)

thread.start_new_thread(lambda: None, ())

ctrl = Ctrl()
while True:
	ctrl.ping()
	time.sleep(10)
