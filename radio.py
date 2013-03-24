#!/usr/bin/env python

import sys
import mpd
import requests

from select import select

def print_at(x, y, text):
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
     sys.stdout.flush()

def main(argv):
    timeout = 5
    prompt = '> '
    max_chars = 10
    freq = 105.1
	freq_changed = True
    min_freq = 88.0
    max_freq = 108.0

    # set raw input mode if relevant
    # it is necessary to make stdin not wait for enter
    try:
        import tty, termios

        prev_flags = termios.tcgetattr(sys.stdin.fileno())
        tty.setraw(sys.stdin.fileno())
    except ImportError:
        prev_flags = None

    buf = ''
    sys.stderr.write(prompt)

    try:
	
		client = mpd.MPDClient()        # create client object
		client.connect("localhost", 6600) # connect to localhost:6600
	
        while True: # main loop
		
			if freq_changed:
				url = "http://radio.7digital.fm/radio/key/"+freq+"/nowplaying"
				print_at (2,1, url)
				r = requests.get("http://radio.7digital.fm/radio/key/105.1/nowplaying").json()
				print_at (2,2, "Now playing: {0}".format(r["artist_name"]))
				url = r["preview_url"]
				print_at (2,3, "Stream url: {0}".format(url))
				pos = r["play_position"]
				print_at (2,4, "Play position: {0}".format(pos))
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
                    freq -= 0.1
					freq_changed = True

                if c == 'd' and freq < max_freq:
                    freq += 0.1
					freq_changed = True

                buf += c
                # auto-output is disabled as well, so you need to print it
                #sys.stderr.write("Type: %s" % ord(c))

                print_at (2, 5, freq))
				
            else:
                # timeout
                break
    except :
        pass
		
	client.stop()
	client.close()
	client.disconnect()

    # restore non-raw input
    if prev_flags is not None:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, prev_flags)
    # and print newline
    sys.stderr.write('\n')

    # now buf contains your input
    # ...

if __name__ == "__main__":
    main(sys.argv[1:])


