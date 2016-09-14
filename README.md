# PaiMorse: Morse module for Python

This code contains

1. a module that generates Morse code (dots and dashes) from strings;
2. an audio module which abstracts the underlying multimedia system. It looks for system-dependent audio modules and chooses one;
3. a module for native CoreAudio (Mac OS X) access;
4. a CLI tool that doubles as a simple example of how to use the modules.

The audio module uses real-time audio generation when possible (e.g. CoreAudio allows it, while NSAudio does not). This is important because correct timing makes a big difference in Morse audio output, in particular when high WPM rates are requested. Starting/stopping is just not good enough.

Toggling the volume/muting the sound would be fast enough, but sounds harsh and noisy at high WPM rates. Our audio module ramps up and down the generated wave for each symbol, so it sounds a lot smoother and symbol recognition is much easier.
