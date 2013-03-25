#!/usr/bin/env python

import sys
import mpd
import requests

from select import select
from sets import Set
from decimal import *
getcontext().prec = 4


def print_at(x, y, text):
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
     sys.stdout.flush()

def cls():
    sys.stderr.write("\x1b[2J\x1b[H")

def good_frequency(selected_freq, all_frequencies):
    #print_at(15,1, "Freq type {0}".format(all_frequencies))
    if selected_freq in all_frequencies:
        #print_at (14,1, "Radio found at {0}".format(selected_freq))
        return True
    
    #print_at (14,1, "No radio found at {0}".format(selected_freq))
    return False

def main(argv):
    cls()

    timeout = 1500
    freq = Decimal(104)
    freq_changed = True
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
                if good_frequency(freq, frequencies):
   	            url = "http://radio.7digital.fm/radio/key/%s/nowplaying" % freq
		    print_at (2,1, url)
		    raw_r = requests.get("http://radio.7digital.fm/radio/key/%s/nowplaying" % freq)
		    r = raw_r.json()
		    print_at (3,1, "Response status: {0}".format(raw_r.status_code))
		    print_at (4,1, "Now playing: {0}".format(r["artist_name"]))
		    url = r["preview_url"]
		    print_at (5,1, "Stream url: {0}".format(url))
		    pos = r["play_position"]
		    print_at (6,1, "Play position: {0}".format(pos))
		    #print client.status()
		    client.command_list_ok_begin() # start a command list
		    client.clear() # insert the update command into the list
		    client.add(url)
		    client.seek(0,pos)
		    client.play()
		    results = client.command_list_end()  # results will be a list with the results			
		    freq_changed = False
			
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
		
    finally:
	client.stop()
	client.close()
	client.disconnect()

	# restore non-raw input
    	if prev_flags is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, prev_flags)
    	# and print newline
        sys.stderr.write('\n')

if __name__ == "__main__":
    main(sys.argv[1:])


