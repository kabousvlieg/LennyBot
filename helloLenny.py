#!/usr/bin/env python
"""
SYNOPSIS

    TODO helloworld [-h,--help] [-v,--verbose] [--version]

DESCRIPTION

    TODO This describes how to use this script. This docstring
    will be printed by the script if there is an error or
    if the user requests help (-h or --help).

EXAMPLES

    TODO: Show some examples of how to use this script.

EXIT STATUS

    TODO: List exit codes

AUTHOR

    TODO: Name <name@example.org>

LICENSE

    This script is in the public domain, free from copyrights or restrictions.

VERSION

    $Id$
"""

import sys, os, traceback, optparse
import time
import pyglet
import pyaudio
import pyaudio
import wave
from sys import byteorder
from array import array
from struct import pack


def exit_callback(dt):
    pyglet.app.exit()

THRESHOLD = 8000
CHUNK_SIZE = 4096
FORMAT = pyaudio.paInt16
RATE = 44100

AUDIOFILES = ["Hello this is Lenny.mp3",
              "Sorry I can barely hear ya there .mp3",
              "Yes yes yes..mp3",
              "Ah good yes yes yes..mp3",
              "Someone did call last week about the same thing was that you.mp3",
              "Sorry what was you name again.mp3",
              "Its funny that you should call because my thirdeldest Larissa....mp3",
              "Im sorry I couldnt quite catch ya there what was that again.mp3",
              "Sorry again.mp3",
              "Could you say that again please.mp3",
              "Yes yes yes..mp3",
              "Sorry which company did you say you were calling from again.mp3",
              "Heres the thing cause the last time someone called up and spoke to me... .mp3",
              "Since you put it that way you have been quite friendly with me here... .mp3",
              "Well with the world finances they way they are....mp3",
              "Well that does sound good you have been very patient with an old man here....mp3"]

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    print("max = " + str(max(snd_data)))
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    r = array('h', [0 for i in xrange(int(seconds*RATE))])
    r.extend(snd_data)
    r.extend([0 for i in xrange(int(seconds*RATE))])
    return r

def record():
    """
    Record a word or words from the microphone and
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the
    start and end, and pads with 0.5 seconds of
    blank sound to make sure VLC et al can play
    it without getting chopped off.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 30:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r

def waitForSilence():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent:
            print("silent " + str(num_silent))
            num_silent += 1
        else:
            print("not silent")
            num_silent = 0;

        if num_silent > 30:
            print("silence detected")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    return

def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

def main ():
    global options, args
    clip_nr = 0
    while 1:
        waitForSilence()
        music = pyglet.resource.media(AUDIOFILES[clip_nr])
        music.play()
        pyglet.clock.schedule_once(exit_callback, music.duration)
        pyglet.app.run()
        clip_nr += 1
        if clip_nr > len(AUDIOFILES) - 1:
            clip_nr = 1


if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'], version='$Id$')
        parser.add_option ('-v', '--verbose', action='store_true', default=False, help='verbose output')
        (options, args) = parser.parse_args()
        #if len(args) < 1:
        #    parser.error ('missing argument')
        if options.verbose: print(time.asctime())
        main()
        if options.verbose: print(time.asctime())
        if options.verbose: print('TOTAL TIME IN MINUTES:',)
        if options.verbose: print((time.time() - start_time) / 60.0)
        sys.exit(0)
    except KeyboardInterrupt as e: # Ctrl-C
        raise e
    except SystemExit as e: # sys.exit()
        raise e
    except Exception as e:
        print('ERROR, UNEXPECTED EXCEPTION')
        print(str(e))
        traceback.print_exc()
        os._exit(1)