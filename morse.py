#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epx@epx.com.br>

import wave, struct, StringIO, math, time, sys

SAMPLING = 22050

code = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
	'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
	'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
	'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
	'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
	'Z': '--..',
	'0': '-----',           ',': '--..--',
	'1': '.----',           '.': '.-.-.-',
	'2': '..---',           '?': '..--..',
	'3': '...--',           ';': '-.-.-.',
	'4': '....-',           ':': '---...',
	'5': '.....',           "'": '.----.',
	'6': '-....',           '-': '-....-',
	'7': '--...',           '/': '-..-.',
	'8': '---..',           '(': '-.--.-',
	'9': '----.',           ')': '-.--.-',
	' ': '',                '_': '..--.-',
	'@': '.--.-.',          '$': '...-..-',
	'&': '.-...',           '!': '-.-.--',
}


def ramp(pos, length):
	'''
	Generates a fadein/fadeout ramp for sound
	'''

	rvolume = 1.0
	fadein = SAMPLING * 0.001
	fadeout = length - fadein
	if pos < fadein:
		rvolume = pos / fadein
	elif pos > fadeout:
		rvolume = (length - pos) / fadein
		
	return rvolume


def generate_wave(freq, volume, duration):
	'''
	Generates a WAV data sequence for the given frequency,
	volume and duration. The output could be written directly
	into a .wav file.
	'''

	wav = StringIO.StringIO()
	f = wave.open(wav, "w")
	f.setnchannels(1)
	f.setsampwidth(2)
	f.setframerate(SAMPLING)
	sduration = int(SAMPLING * duration)
	samples = [ int(math.sin(freq * (n / float(SAMPLING)) * math.pi * 2) 
			* 32767 * volume * ramp(n, sduration)) \
			for n in range(0, sduration) ]
	f.writeframes(struct.pack('%dh' % len(samples), *samples))
	data = wav.getvalue()

	if not cfg['wavheader']:
		data = data[44:]

	return data

def generate_silence(duration):
	'''
	Generates a WAV data silence.
	'''

	wav = StringIO.StringIO()
	f = wave.open(wav, "w")
	f.setnchannels(1)
	f.setsampwidth(2)
	f.setframerate(SAMPLING)
	sduration = int(SAMPLING * duration)
	samples = [ 0 for n in range(0, sduration) ]
	f.writeframes(struct.pack('%dh' % len(samples), *samples))
	data = wav.getvalue()

	if not cfg['wavheader']:
		data = data[44:]

	return data


nonascii = (	(u'çÇ©',        'C'),
		(u'ñÑ',         'N'),
		(u'ÁÃÀÂÄáãàâä', 'A'),
		(u'ÉÈÊËéèêë',   'E'),
		(u'ÍÌÎÏíìîï',   'I'),
		(u'ÓÒÔÖÕóòôöõ', 'O'),
		(u'ÚÙÛÜúùûü',   'U'),
		(u'',		'AP'))


def cast_alphabet(input):
	'''
	Filters a text message for Morse encoding.
	The input should be Unicode.
	Characters that have no Morse symbol are removed.

	Some Latin characters like "é" are converted to the
	non-accented version ("e") to mitigate the loss. See
	module.nonascii tuple for details.
	'''

	input = input.upper()
	output = ""
	for c in input:
		for chars, replacement in nonascii:
			if c in chars:
			    c = replacement
			    break
		if c in code:
			output += c
	return output


cfg = {}
cfg['.'] = 1.0


class Beeper(object):
	def __init__(self):
		pass

	def play(self, bit):
		print bit
		time.sleep(cfg['duration' + bit])

	def wait(self):
		pass


cfg['audio'] = Beeper()


if sys.platform == 'darwin':
	from AppKit import NSObject, NSSound, NSData
	from PyObjCTools import AppHelper

	class MacOSXBeeper(NSObject, object):
	    	def init(self):
			cfg['queue'] = []
			cfg['playing'] = False
			return self

		def play(self, bit):
			cfg['queue'] += bit
			self.do_play()

		def do_play(self):
			if cfg['playing'] or not cfg['queue']:
				return
			cfg['playing'] = True
			bit = cfg['queue'][0]
			del cfg['queue'][0]
			wavdata = cfg["sample" + bit]
			self.impl = NSSound.alloc()
			data = NSData.alloc().initWithBytes_length_(wavdata, len(wavdata))
			self.impl.initWithData_(data)
			self.impl.setDelegate_(self)
			self.impl.play()

		def sound_didFinishPlaying_(self, s, p):
			cfg['playing'] = False
			if cfg['queue']:
				self.do_play()
			else:
				AppHelper.stopEventLoop()

		def wait(self):
			AppHelper.runConsoleEventLoop()
			pass

	cfg['audio'] = MacOSXBeeper.new()
	cfg['wavheader'] = True


elif sys.platform == 'linux2':
	import ossaudiodev
	import threading

	class OSSBeeper(Beeper):
		def open_audio(self):
			if self.impl:
				self.close_audio()
			self.impl = ossaudiodev.open("/dev/dsp", "w")
			self.impl.setparameters(ossaudiodev.AFMT_S16_LE, 1, SAMPLING)
			self.impl.nonblock()

		def close_audio(self):
			if self.impl:
				self.impl.close()
			self.impl = None

		def __init__(self):
			self.impl = None
			self.buf = ""
			self.open_audio()
			self.drain = self.impl.bufsize()

		def play(self, bit):
			if not self.impl:
				self.open_audio()

			self.buf += cfg["sample" + bit]

			if len(self.buf) > self.drain:
				# Let's begin to play something
				if self.impl.obuffree() > 0:
					print "Non-blocking write"
					written = self.impl.write(self.buf)
					print "\t %d samples" % written
					self.buf = self.buf[written:]

			if len(self.buf) > 10 * self.drain:
				# Does not let buffer grow too long
				length = 5 * self.drain
				data = self.buf[:length]
				self.buf = self.buf[length:]
				print "Blocking write of %d smamples" % length
				self.impl.writeall(data)

		def wait(self):
			if self.buf:
				# Make buffer empty
				data = self.buf
				self.buf = ""
				self.impl.writeall(data)

	cfg['audio'] = OSSBeeper()
	cfg['wavheader'] = False


def make_audio_samples():
	'''
	Prepares audio samples.
	'''

	dot_duration = cfg['DOT_LENGTH'] * cfg['.']
	dash_duration = cfg['DOT_LENGTH'] * cfg['-']
	space_duration = cfg['DOT_LENGTH'] * cfg[' ']
	interbit_duration = cfg['DOT_LENGTH'] * cfg['i']

	cfg['sample.'] = generate_wave(cfg['freq'], cfg['volume'], dot_duration)
	cfg['sample-'] = generate_wave(cfg['freq'], cfg['volume'], dash_duration)
	cfg['sample '] = generate_silence(space_duration)
	cfg['samplei'] = generate_silence(interbit_duration)

	cfg['duration.'] = dot_duration
	cfg['duration-'] = dash_duration
	cfg['duration '] = space_duration
	cfg['durationi'] = interbit_duration

def config(freq=0, volume=0, wpm=0, dash=0, interbit=0, intersymbol=0):
	'''
	Configure Morse code sound and rhythm.
	Passing 0 for any parameter means that it will not be changed,
	leaving the default (or the last configured) value.

	freq: beep frequency, in Hz. Default 800Hz

	volume: volume between 0.0 and 1.0. Default: 0.25

	wpm: speed in words per minute. Default: 20.0

	     Dot sound length will be made = 1.425 / wpm,
	     so e.g. 20 WPM translates to a dot of ~70ms,
	     and all the rest will be proportional to this.

	dash: dash sound length, in dots. Default: 3 times a dot.

	interbit: silence between Morse symbols, in dots. Default: 0.6 dots.

	intersymbol: silence between two letters, in dots. Default: 2 dots.
	'''

	if wpm >= 1:
		cfg['WPM'] = float(wpm)
		cfg['DOT_LENGTH'] = 1.425 / wpm

	if dash >= 1.0 and dash < 10:
		cfg['-'] = float(dash)

	if interbit > 0 and interbit < 10:
		cfg['i'] = float(interbit)

	if intersymbol > 0 and intersymbol < 10:
		cfg[' '] = float(intersymbol)

	if freq > 0 and freq <= 11025:
		cfg['freq'] = float(freq)

	if volume > 0 and volume <= 1.0:
		cfg['volume'] = float(volume)

	make_audio_samples()


def encode_morse(input):
	''' Converts a text message to Morse code elements.
	    Three characters can be elements:
		. 	point		dot
		-	hyphen		dash
			space 		silence between letters
	    Two Morse spaces are put between words (for every text space)
	'''

	# Coerce the message into the supported alphabet.
	# See "nonascii" tuple.
	input = cast_alphabet(input)
	output = ""
	for c in input:
		try:
			k = code[c]
		except KeyError:
			continue
		output += k
		output += ' '
	return input, output


def play_morse_bits(bits):
	'''
	Plays a Morse 'tape' with dashes, dots etc.
	The accepted format is the one returned by encode_morse().
	'''

	lastbit = ''
	for bit in bits:
		if lastbit in ".-":
			cfg['audio'].play('i')
		cfg['audio'].play(bit) 
		lastbit = bit 
	cfg['audio'].wait()


def play(text):
	'''
	Plays a text message as Morse code.
	This is a convenience function that takes care of
	text -> morse encoding.
	'''
	play_morse_bits(encode_morse(text))


config(800, 0.25, 12, 3, 0.6, 2)
