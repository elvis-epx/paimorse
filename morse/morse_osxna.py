#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epx@epx.com.br>

from AppKit import NSObject, NSSound, NSData
from PyObjCTools import AppHelper

local_data = {}

class MacOSXBeeper(NSObject, object):
    	def init(self):
		local_data['queue'] = []
		local_data['playing'] = False
		return self

	def play(self, sample):
		local_data['queue'].append(sample)
		self.do_play()

	def do_play(self):
		if local_data['playing'] or not local_data['queue']:
			return
		local_data['playing'] = True
		sample = local_data['queue'][0]
		del local_data['queue'][0]
		self.impl = NSSound.alloc()
		data = NSData.alloc().initWithBytes_length_(sample, len(sample))
		self.impl.initWithData_(data)
		self.impl.setDelegate_(self)
		self.impl.play()

	def sound_didFinishPlaying_(self, s, p):
		local_data['playing'] = False
		if local_data['queue']:
			self.do_play()
		else:
			AppHelper.stopEventLoop()

	def wait(self):
		AppHelper.runConsoleEventLoop()
		pass


def factory(sampling_rate):
	return MacOSXBeeper.new()
