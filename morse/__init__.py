#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Elvis Pfutzenreuter <epx@epx.com.br>

import wave, struct, StringIO, math, time, sys
import morse_audio

SAMPLING = 44100

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

def generate_float_wave(freq, volume, duration):
	sduration = int(SAMPLING * duration)

	if volume > 0.0:
		samples = [ math.sin(freq * (n / float(SAMPLING))
				     * math.pi * 2) 
				* volume * ramp(n, sduration) \
				for n in range(0, sduration) ]
	else:
		samples = [ 0.0 for n in range(0, sduration) ]

	return samples


def generate_wave(freq, volume, duration):
	'''
	Generates a WAV data sequence for the given frequency,
	volume and duration. The output could be written directly
	into a .wav file (except when 'float' format is requested).
	'''

	samples = generate_float_wave(freq, volume, duration)

	if cfg['wavformat'] == 'str':
		samples = [ int(n * 32767) for n in samples ]
		wav = StringIO.StringIO()
		f = wave.open(wav, "w")
		f.setnchannels(1)
		f.setsampwidth(2)
		f.setframerate(SAMPLING)
		f.writeframes(struct.pack('%dh' % len(samples), *samples))
		samples = wav.getvalue()

		if not cfg['wavheader']:
			samples = samples[44:]

	return samples


def generate_silence(duration):
	'''
	Generates a WAV data silence.
	'''
	return generate_wave(0.0, 0.0, duration)


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

morse_audio.configure(SAMPLING, cfg)


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

	     Dot sound length will be made = 1.42 / wpm,
	     so e.g. 20 WPM translates to a dot of ~70ms,
	     and all the rest will be proportional to this.

	dash: dash sound length, in dots. Default: 3 times a dot.

	interbit: silence between Morse symbols, in dots. Default: 0.6 dots.

	intersymbol: silence between two letters, in dots. Default: 2 dots.
	'''

	if wpm >= 1:
		cfg['WPM'] = float(wpm)
		cfg['DOT_LENGTH'] = 1.42 / wpm / cfg['compensation']

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
			cfg['audio'].play(cfg['sample' + 'i'])
		cfg['audio'].play(cfg['sample' + bit]) 
		lastbit = bit 
	cfg['audio'].eol_flush()


def play(text):
	'''
	Plays a text message as Morse code.
	This is a convenience function that takes care of
	text -> morse encoding.
	'''
	play_morse_bits(encode_morse(text))


def final_flush():
	'''
	Makes sure all pending audio has been played.
	Blocks until audio has been played.
	'''
	cfg['audio'].final_flush()


config(800, 0.25, 12, 3, 0.6, 2)
