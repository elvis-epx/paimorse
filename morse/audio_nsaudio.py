#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epxx@epxx.co>

from AppKit import NSObject, NSSound, NSData
from PyObjCTools import AppHelper

class MacOSXBeeper(NSObject, object):
    	def init(self):
		self.queue = []
		self.playing = False
		self.loop = False
		return self

	def play(self, sample):
		self.queue.append(sample)
		if len(self.queue) > 10:
			self.do_play()

	def do_play(self):
		if self.playing or not self.queue:
			return
		self.playing = True
		sample = self.queue[0]
		del self.queue[0]
		self.impl = NSSound.alloc()
		data = NSData.alloc().initWithBytes_length_(sample, len(sample))
		self.impl.initWithData_(data)
		self.impl.setDelegate_(self)
		self.impl.play()

	def sound_didFinishPlaying_(self, s, p):
		self.playing = False
		if self.queue:
			self.do_play()
		elif self.loop:
			AppHelper.stopEventLoop()

	def eol_flush(self):
		if self.queue:
			self.do_play()
		if self.playing:
			self.loop = True
			AppHelper.runConsoleEventLoop()
			self.loop = False

	def final_flush(self):
		self.eol_flush()


def factory(sampling_rate):
	return MacOSXBeeper.new()
