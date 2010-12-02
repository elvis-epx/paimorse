#!/usr/bin/env python

import thread
import coreaudio # http://wiki.python.org/moin/MacPython/CoreAudio
import time

class Ctrl(object):
	def callback(self):
		# called in another thread context!
		return self.silence

	def __init__(self):
		audio_id, sampling_rate, chunksize = coreaudio.initAudio()
		self.silence = [0.0 for i in range(0, chunksize)]
		coreaudio.installAudioCallback(audio_id, self)

	def stop(self):
		coreaudio.stopAudio(self)

# Have to initialize the threading mechanisms in order for PyGIL_Ensure to work
thread.start_new_thread(lambda: None, ())

try:
	ctrl = Ctrl()
	time.sleep(999999)
except KeyboardInterrupt:
	ctrl.stop()
	time.sleep(0.1)
