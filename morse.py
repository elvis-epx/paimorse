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


def ramp(pos, length, dot_length):
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


def generate_wave(freq, volume, duration, dot_duration, header):
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
	dot_sduration = int(SAMPLING * dot_duration)
	samples = [ int(math.sin(freq * (n / float(SAMPLING)) * math.pi * 2) 
			* 32767 * volume * ramp(n, sduration, dot_sduration)) \
			for n in range(0, sduration) ]
	f.writeframes(struct.pack('%dh' % len(samples), *samples))
	data = wav.getvalue()
	if not header:
		data = data[44:]
	return data


nonascii = (	(u'çÇ©',       'C'),
		(u'ñÑ',         'N'),
		(u'ÁÃÀÂÄáãàâä', 'A'),
		(u'ÉÈÊËéèêë',   'E'),
		(u'ÍÌÎÏíìîï',   'I'),
		(u'ÓÒÔÖÕóòôöõ', 'O'),
		(u'ÚÙÛÜúùûü',   'U'))


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
cfg['sample.'] = None
cfg['sample-'] = None
cfg['sample '] = None
cfg['.'] = 1.0


class Beeper(object):
	def __init__(self, duration, dot_duration):
		self.duration = duration

	def play(self):
		time.sleep(self.duration)


if sys.platform == 'darwin':
	from AppKit import NSSound, NSData

	class MacOSXBeeper(Beeper):
		def __init__(self, duration, dot_duration):
			Beeper.__init__(self, duration, dot_duration)
			self.impl = NSSound.alloc()
			wavdata = generate_wave(cfg['freq'], cfg['volume'],
						duration, dot_duration, True)
			data = NSData.alloc().initWithBytes_length_(wavdata, len(wavdata))
			self.impl.initWithData_(data)
		
		def play(self):
			self.impl.setCurrentTime_(0)
			self.impl.play()
			Beeper.play(self)

	cfg['class'] = MacOSXBeeper


elif sys.platform == 'linux2':
	import ossaudiodev

	class LinuxBeeper(Beeper):
		def __init__(self, duration, dot_duration):
			Beeper.__init__(self, duration, dot_duration)
			self.wavdata = generate_wave(cfg['freq'], cfg['volume'],
						duration, dot_duration, False)
			self.helper = None

		def play(self):
			self.impl.writeall(self.wavdata)
			self.impl.sync()

		def helper_finished(self):
			self.helper = None

	LinuxBeeper.impl = ossaudiodev.open("w")
	LinuxBeeper.impl.setparameters(SAMPLING, 16, 1, ossaudiodev.AFMT_S16_LE)
	LinuxBeeper.nonblock()

	cfg['class'] = LinuxBeeper


def config_sound():
	'''
	Prepares the audio player. The result is put in
	module.cfg['sample.'] and module.cfg['sample-']. 

	The sampler objects will support a very simple interface:
	async play().
	'''

	dash_duration = cfg['DOT_LENGTH'] * cfg['-']
	dot_duration = cfg['DOT_LENGTH'] * cfg['.']
	space_duration = cfg['DOT_LENGTH'] * cfg[' ']
	cfg['sample.'] = cfg['class'](dot_duration, dot_duration)
	cfg['sample-'] = cfg['class'](dash_duration, dot_duration)
	cfg['sample '] = Beeper(space_duration, dot_duration)


def config(freq=0, volume=0, wpm=0, dash=0, interbit=0, intersymbol=0):
	'''
	Configure Morse code sound and rhythm.
	Passing 0 for any parameter means that it will not be changed,
	leaving the default (or the last configured) value.

	freq: beep frequency, in Hz. Default 800Hz

	volume: volume between 0.0 and 1.0. Default: 0.25

	wpm: speed in words per minute. Default: 20.0

	     Dot sound length will be made = 1.2 / wpm,
	     so e.g. 20 WPM translates to a dot of 60ms,
	     and all other times will be proportional to this.

	dash: dash sound length, in dots. Default: 3 times a dot.

	interbit: silence between Morse symbols, in dots. Default: 0.5 dots.

	intersymbol: silence between two letters, in dots. Default: 1.0 dot.
	'''

	if wpm >= 1:
		cfg['WPM'] = float(wpm)
		cfg['DOT_LENGTH'] = 1.2 / wpm
		cfg['sample.'] = None

	if dash >= 1.0 and dash < 10:
		cfg['-'] = float(dash)
		cfg['sample.'] = None

	if interbit > 0 and interbit < 10:
		cfg['interbit'] = float(interbit)
		cfg['sample.'] = None

	if intersymbol > 0 and intersymbol < 10:
		cfg[' '] = float(intersymbol)
		cfg['sample.'] = None

	if freq > 0 and freq <= 11025:
		cfg['freq'] = float(freq)
		cfg['sample.'] = None

	if volume > 0 and volume <= 1.0:
		cfg['volume'] = float(volume)
		cfg['sample.'] = None


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
	if not cfg['sample.']:
		config_sound()

	lastbit = ''
	for bit in bits:
		try:
			beeper = cfg['sample' + bit]
		except KeyError:
			continue

		if lastbit in ".-":
			time.sleep(cfg['interbit'] * cfg['DOT_LENGTH'])

		beeper.play() # blocks

		lastbit = bit 


def play(text):
	'''
	Plays a text message as Morse code.
	This is a convenience function that takes care of
	text -> morse encoding.
	'''
	play_morse_bits(encode_morse(text))


config(800, 0.25, 12, 3, 0.6, 2.5)
