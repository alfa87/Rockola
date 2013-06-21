
import json
import time

from multiprocessing import Process
from subprocess import Popen
from urllib import urlencode
from urllib2 import urlopen

from msgs_queue import queue_manager

class VLCController(object):

    PORT = '10333'

    def __init__(self):
        '''
            start the VLC process
        '''
        self.p = Popen(['vlc',
                        '-I http',
                        '--http-host', '0.0.0.0',
                        '--http-port', self.PORT])
        self.base_url = 'http://localhost:%s/requests/status.json' % self.PORT
        self.wd = NextSongWatcher()
        self.wd.run()

    def add_song(self, path, play_it_now=False):
        '''
            Add a new song to the playlist and play it
        '''
        data = {'command': 'in_play',
                'input': 'file://' + path}
        s = '%s?%s' % (self.base_url, urlencode(data))
        urlopen(s)

    def get_reamining_time(self):
        status_raw = urlopen(self.base_url).read()
        status = json.loads(status_raw)
        if 'time' in status:
            return status['length'] - status['time']
        else:
            return 0


class ShivaClient(object):

    PORT = '9002'
    URL = 'avioncito'
    def __init__(self):
        self.base_url =  'http://%s:%s/' %(self.URL,self.PORT)
        self.artists = {}
        for artist in self.get_artists():
            artist_id, name = artist['id'], artist['name']
            self.artists[artist_id] = name
        self.artists[None] = ''

    def _request(self, command):

        r = urlopen(self.base_url + command)
        data = r.read()
        return json.loads(data)

    def get_tracks(self, ids):

        tracks = self._request('tracks')

        response = {}
        for track in tracks:
            track_id = track['id']
            if track_id in ids:
                track_title = track['title']
                if track['artist'] is not None:
                    artist_id = track['artist']['id']
                else:
                    artist_id = None
                artist = self.artists[artist_id]
                response[track_id] = {'title': track_title,
                                      'artist': artist}
        return response

    def get_artists(self):
        return self._request('artists')

class NextSongWatcher(object):

    def __init__(self, vlcc):
        self.control_name = queue_manager.get_queue_name('control')
        self.running = True
        self.sender = queue_manager.Queue()
        self.vlcc = vlcc

    def receive_loop(self):
        while self.running:
            remaining_time = self.vlcc.remaining_time()
            print remaining_time
            if remaining_time < 10:
                data = {'timestamp': int(time.time()),
                        'operation': 'nueva_cancion'}
                self.sender.send(self.control_name, json.dumps(data))
                time.sleep(20)

            time.sleep(5)

    def run(self):
        p = Process(target=self.receive_loop)
        p.start()

    def stop(self):
        self.stopping = False

if __name__ == '__main__':
    pass

