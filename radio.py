#!/usr/bin/env python

import sys
import mpd
import requests
import pygame

from select import select
from sets import Set
from decimal import *
getcontext().prec = 4

pygame.init()
pygame.mixer.init()

s = pygame.mixer.Sound('noise.ogg')
noise = s.play(loops=-1)

def print_at(x, y, text):
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
     sys.stdout.flush()

def cls():
    sys.stderr.write("\x1b[2J\x1b[H")

def good_frequency(selected_freq, all_frequencies):
    all_frequencies = sorted(all_frequencies)
    print_at(15,1, "Freq type {0}".format(all_frequencies))
    prev_freq = 0
    for f in all_frequencies:
    	if (f >= selected_freq):
            if (f-selected_freq < selected_freq-prev_freq):
	        print_at (14,1, "Radio found at {0}, {1} difference".format(f,f-selected_freq))
		return [f, f-selected_freq]
	    else:
                print_at (14,1, "Radio found at {0}, {1} difference".format(prev_freq,selected_freq-prev_freq))
                return [prev_freq, selected_freq-prev_freq]
	prev_freq = f
    
    return [0,1000]


def main(argv):
    cls()

    timeout = 1500
    freq = Decimal(104)
    freq_changed = True
    tuned_in = 0
    min_freq = Decimal(88.0)
    max_freq = Decimal(108.0)
    frequencies = Set()

    raw_r = requests.get("http://radio.7digital.fm/radio/frequencies")
    r = raw_r.json()
    for f in r:
	frequencies.add(Decimal(f["key"]))
           
    for f in frequencies:
        print f

    # set raw input mode if relevant
    # it is necessary to make stdin not wait for enter
    try:
        import tty, termios

        prev_flags = termios.tcgetattr(sys.stdin.fileno())
        tty.setraw(sys.stdin.fileno())
    except ImportError:
        prev_flags = None

    try:
	client = mpd.MPDClient()        # create client object
	client.connect("localhost", 6600) # connect to localhost:6600
	
        while True: # main loop
	    	
	    if freq_changed:
                cls()
                print_at (1, 1, "Frequency: %s " % freq)
		closest_good_freq = good_frequency(freq, frequencies)
		gfreq = closest_good_freq[0]
		gfreq_diff = closest_good_freq[1]
                if gfreq_diff<=1:
		    if (tuned_in != gfreq):
                        url = "http://radio.7digital.fm/radio/key/%s/nowplaying" % gfreq
     	                print_at (22,1, url)
                    	raw_r = requests.get("http://radio.7digital.fm/radio/key/%s/nowplaying" % gfreq)
                    	r = raw_r.json()
                    	print_at (23,1, "Response status: {0}".format(raw_r.status_code))
                    	print_at (24,1, "Now playing: {0}".format(r["artist_name"]))
                    	url = r["preview_url"]
                    	print_at (25,1, "Stream url: {0}".format(url))
                    	pos = r["play_position"]
                    	print_at (26,1, "Play position: {0}".format(pos))
                    	#print client.status()
 
		    	client.command_list_ok_begin() # start a command list
		    	client.clear() # insert the update command into the list
		    	client.add(url)
		    	client.seek(0,pos)
		    	client.play()
		    	results = client.command_list_end()  # results will be a list with the results			
			tuned_in = gfreq
		    freq_changed = False
		    client.setvol(100-int(gfreq_diff*200))
		    noise.set_volume(gfreq_diff)
		else:
		    if tuned_in>0:
			noise.set_volume(0.9)
			tuned_in = 0
			client.setvol(0)
	    print_at (30,1, "MPD state {0}".format(client.status()["state"]))
	    print_at (31,1, "MPD volume {0}".format(client.status()["volume"]))
	    if (client.status()["state"]=="stop"):
		tuned_in = 0
		freq_changed=True
		
            rl, wl, xl = select([sys.stdin], [], [], timeout)
            if rl: # some input
                c = sys.stdin.read(1)
                # you will probably want to add some special key support
                # for example stop on enter:
                if c == 'x':
                    break

                if c == 'a' and freq > min_freq:
                    freq -= Decimal(0.1)
    	    	    freq_changed = True

                if c == 'd' and freq < max_freq:
                    freq += Decimal(0.1)
		    freq_changed = True
				
            else:
                # timeout
                break
        client.stop()
        client.close()
        client.disconnect()		


    finally:
#	client.stop()
#	client.close()
#	client.disconnect()

	# restore non-raw input
    	if prev_flags is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, prev_flags)
    	# and print newline
        sys.stderr.write('\n')

if __name__ == "__main__":
    main(sys.argv[1:])


