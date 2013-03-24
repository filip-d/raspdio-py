import mpd
import requests

client = mpd.MPDClient()        # create client object
client.connect("localhost", 6600) # connect to localhost:6600
print client.mpd_version                # print the mpd version
#print client.cmd("one", 2)     # print result of the command "cmd one 2"
#client.close()                 # send the close command
#client.disconnect()            # disconnect from the server

r = requests.get("http://radio.7digital.fm/radio/key/105.1/nowplaying")

print r.json()["preview_url"]
print r.json()["artist_name"]

freq = raw_input("Enter radio frequency (e.g. 105.6) or type exit: ")
while freq!="exit":

        url = "http://radio.7digital.fm/radio/key/"+freq+"/nowplaying"
        print "radio url: ", url
        r = requests.get("http://radio.7digital.fm/radio/key/105.1/nowplaying").json()
        print "Now playing: ", r["artist_name"]
        url = r["preview_url"]
        print "Stream url: ", url
        pos = r["play_position"]
        print "Play position: ", pos
        print client.status()
        client.command_list_ok_begin() # start a command list
        client.clear() # insert the update command into the list
        client.add(url)
        client.seek(0,pos)
        client.play()
        results = client.command_list_end()  # results will be a list with the results
        freq = raw_input("Enter URL or type exit: ")

client.stop()
client.close()
client.disconnect()
