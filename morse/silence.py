#!/usr/bin/env python

import thread
import coreaudio
import time

class Ctrl(object):
	def callback(self):
		# Called in another thread's context
		return self.silence

	def close(self):
		coreaudio.stopAudio(self)

	def __init__(self):
		self.buf = []
		self.audio_id, self.sampling_rate, self.chunksize = coreaudio.initAudio()
		self.silence = [0.0 for i in range(0, self.chunksize)]

	def open(self):
		coreaudio.installAudioCallback(self.audio_id, self)

# Have to initialize the threading mechanisms in order for PyGIL_Ensure to work
thread.start_new_thread(lambda: None, ())

try:
	ctrl = Ctrl()
	time.sleep(1)
	ctrl.open()
	time.sleep(999999)
except KeyboardInterrupt:
	ctrl.close()
