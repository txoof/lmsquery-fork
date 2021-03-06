#!/usr/bin/env python
#!/usr/bin/env python
# coding: utf-8


# In[14]:


#get_ipython().run_line_magic('alias', 'nbconvert nbconvert ./lmsquery.ipynb')
#get_ipython().run_line_magic('nbconvert', '')




# In[13]:


import requests

import json
import datetime

# from . import const
# from . import scanLMS

import socket

try:
    from . import const
except ImportError as e:
    import const

import logging




# In[7]:


# logger = logging.getLogger(__name__)
# logger.root.setLevel('DEBUG')




# In[10]:


class LMSQuery(object):
    def __init__(self, host=None, port=None, player_name=None, player_id=None, lms_servers=None):
        self.lms_servers = lms_servers
        self.host = host
        self.port = port
        self.server_base_url = f'http://{self.host}:{self.port}/'
        self.server_url = f'{self.server_base_url}jsonrpc.js'
        self.player_id = player_id
        self.player_name = player_name

    @property
    def lms_servers(self):
        return self._lms_servers
    
    @lms_servers.setter
    def lms_servers(self, lms_servers):
        if not lms_servers:
#             lms_servers = scanLMS.scanLMS()
            # scan the network for lms servers
            lms_servers = self.scanLMS()
        if not lms_servers:
            lms_servers = []
            logging.warning('no servers found on local network')
            lms_servers.append({'host': None, 'port': const.LMS_PORT})
        self._lms_servers = lms_servers
    
    @property
    def player_name(self):
        '''set the human readable player name
            also attempt to find a matching playerid and set that 
        
        Args:
            player_name(`str`): string matching human readable player name
            
        Sets:
            player_name
            player_id(`str`): mac address of player (if found)
        '''
        return self._player_name
    
    @player_name.setter
    def player_name(self, player_name):
        if player_name:
            self._player_name = player_name
            # set player id if at least one host was found
            for p in self.get_players():
                if 'name' in p and 'playerid' in p:
                    if p['name'] == player_name:
                        logging.debug(f'found player "{player_name}" on server: {self.host}')
                        self.player_id = p['playerid']
                
            
            # only try to get players if there is a host set
#             for each in self.lms_servers:
#                 if self.lms_servers[each]['host']:
#                     for p in self.get_players():
#                         if 'name' in p and 'playerid' in p:
#                             if p['name'] == player_name:
#                                 self.player_id = p['playerid']
#                 else:
#                     self.player_id = None
        else:
            self._player_name = None
    
    @property
    def host(self):
        return self._host
    
    @host.setter
    def host(self, host):
        if not host:
            host = self.lms_servers[0]['host']
            logging.debug(f'setting LMS Server to first found: {host}')
        self._host = host     
            
    @property
    def port(self):
        return self._port
    
    @port.setter
    def port(self, port):
        if not port:
            port = self.lms_servers[0]['port']
        self._port = port

    def scanLMS(self, timeout=None):
        '''Search local network for Logitech Media Servers

        Based on netdisco/lms.py by cxlwill - https://github.com/cxlwill

        Args:
          timeout (int): timeout seconds

        Returns:
          list: Dictionary of LMS Server IP and listen ports

        '''
        lmsIP  = '<broadcast>'
    #     lmsPort = 3483
        lmsPort = const.LMS_BRDCST_PORT
    #     lmsMsg = b'eJSON\0'
        lmsMsg = const.LMS_BRDCST_MSG
    #     lmsTimeout = 2
        # search for servers unitl timeout expires
        if timeout:
            lmsTimeout = timeout
        else:
            lmsTimeout = const.LMS_BRDCST_TIMEOUT

        entries = []

        mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        mySocket.settimeout(lmsTimeout)
        mySocket.bind(('', 0))
        logging.debug(f'searching for servers for {lmsTimeout} seconds')
        try:
            mySocket.sendto(lmsMsg, (lmsIP, lmsPort))
            while True: # loop until the timeout expires
                try:
                    data, address = mySocket.recvfrom(1024) # read 1024 bytes from the socket
                    if data and address:
                        port = None
                        if data.startswith(b'EJSON'):
                            position = data.find(b'N')
                            length = int(data[position+1:position+2].hex())
                            port = int(data[position+2:position+2+length])
                            entries.append({'host': address[0], 'port': port})

                except socket.timeout:
                    if len(entries) < 1:
                        logging.warning(f'server search timed out after {lmsTimeout} seconds with no results')
                    break            
                except OSError as e:
                    logging.error(f'error opening socket: {e}')
        finally:
            mySocket.close()
        return(entries)

        
###############################################################################
# Generic query
###############################################################################s
    def query(self, player_id="", *args):
        params = json.dumps({'id': 1, 'method': 'slim.request',
                             'params': [player_id, list(args)]})
        r = requests.post(self.server_url, params)
        return json.loads(r.text)['result']

###############################################################################
# Server commands
###############################################################################
    def rescan(self):
        return self.query("", "rescan")

    def get_server_status(self):
        return self.query("", "serverstatus", 0, 99)

    def get_artists(self):
        return self.query("", "artists", 0, 9999)['artists_loop']

    def get_artist_count(self):
        return len(self.get_artists())

    def get_radios_count(self):
        return self.query("", "favorites", "items")['count']

    def get_player_count(self):
        return self.query("", "player", "count", "?")['_count']

    def get_players(self):
        players = self.get_server_status()
        if len(players):
            players = players['players_loop']
        return players

    def search(self, searchstring, count=9999):
        return self.query('', "search", 0, count, "term:" + searchstring)

    def search_tracks(self, searchstring, count=9999):
        result = self.search(searchstring, count)
        if 'tracks_loop' in result:
            response = {"tracks_count": result['tracks_count'],
                    "tracks_loop": result['tracks_loop']}
        else:
            response = {"tracks_count": 0}
        return response

    def search_albums(self, searchstring, count=9999):
        result = self.search(searchstring, count)
        if 'albums_loop' in result:
            response = {"albums_count": result['albums_count'],
                    "albums_loop": result['albums_loop']}
        else:
            response = {"albums_count": 0}
        return response

    def search_contributors(self, searchstring, count=9999):
        result = self.search(searchstring, count)
        if 'contributors_loop' in result:
            response = {"contributors_count": result['contributors_count'],
                    "contributors_loop": result['contributors_loop']}
        else:
            response = {"contributors_count": 0}
        return response

    def search_players(self, searchstring, count=9999):
        players = self.get_players()
        result = []
        count = 0
        for player in players:
            for value in list(player.values()):
                if(searchstring.lower() in str(value).lower()):
                    result.append(player)
                    count = count + 1
        if count > 0:
            response = {"players_count": count, "players_loop": result}
        else:
            response = {"players_count": count}
        return response

    def now_playing(self, player_id=''):
        '''
        returns currently playing track including following information:
          * album
          * artist
          * artwork_url (if available)
          * duration (seconds)
          * genre
          * coverid
          * id
          * title
        '''
        if not player_id:
            player_id = self.player_id
        now_playing_info ={}
        
        #keys from status dict to return in the now-playing dictionary
        status_keys = ['time', 'mode']

        status = self.query(player_id, 'status')
        playing_track = self.query(player_id, 'status', int(status['playlist_cur_index']), 1, '-')['playlist_loop'][0]
        track_id = playing_track['id']
        # query songinfo tags: a - artist, c - coverid; d - duration; e - album_id; g - genre; l - album name
        songinfo = self.query('', 'songinfo', 0, 100, 'track_id:'+str(track_id), 'tags:a,c,d,e,g,l')['songinfo_loop']

        for each in songinfo:
            for key in each:
                now_playing_info[key] = each[key]
        # set default cover id to 0 (static server default image)
        coverid = 0
        if 'coverid' in now_playing_info:
            # handle invalid coverids that show up as negative nubmers
            if now_playing_info['coverid'].startswith('-'):
                pass
            else:
                coverid = now_playing_info['coverid']
        now_playing_info['artwork_url'] = f'{self.server_base_url}music/{coverid}/cover.jpg'
        
        
        for key in status_keys:
            if key in status:
                now_playing_info[key] = status[key]
            else:
                now_playing_info[key] = None

        return(now_playing_info)

###############################################################################
# Player commands
###############################################################################
    def set_power(self, player_id, power=1):
        self.query(player_id, "power", power)

    def set_power_all(self, power=1):
        players = self.get_players()
        for player in players:
            self.set_power(player['playerid'], power)

    def play_album(self, player_id, album_id):
        return self.query(player_id, "playlistcontrol", "cmd:load",
                          "album_id:" + str(album_id))

    def play_radio(self, player_id, radio):
        return self.query(player_id, "favorites", "playlist", "play",
                          "item_id:" + str(radio))

    def pause(self, player_id):
        return self.query(player_id, "pause")

    def skip_songs(self, player_id, amount=1):
        if amount > 0:
            amount = "+" + str(amount)
        else:
            amount = str(amount)
        return self.query(player_id, "playlist", "index", amount)

    def previous_song(self, player_id):
        return self.skip_songs(player_id, -1)

    def next_song(self, player_id):
        return self.skip_songs(player_id)

    def get_volume(self, player_id):
        volume = self.query(player_id, "mixer", "volume", "?")
        if len(volume):
            volume = volume['_volume']
        else:
            volume = 0
        return volume

    def set_volume(self, player_id, volume):
        self.query(player_id, "mixer", "volume", volume)

    def get_current_song_title(self, player_id):
        title = self.query(player_id, "current_title", "?")
        if len(title):
            title = title['_current_title']
        else:
            title = ""
        return title

    def get_current_artist(self, player_id):
        artist = self.query(player_id, "artist", "?")
        if len(artist):
            artist = artist['_artist']
        else:
            artist = ""
        return artist

    def get_current_album(self, player_id):
        album = self.query(player_id, "album", "?")
        if len(album):
            album = album['_album']
        else:
            album = ""
        return album

    def get_current_title(self, player_id):
        title = self.query(player_id, "title", "?")
        if len(title):
            title = title['_title']
        else:
            title = ""
        return title

    def get_current_radio_title(self, player_id, radio):
        return self.query(player_id, "favorites",
                          "items", 0, 99)['loop_loop'][radio]['name']

    def is_playing_remote_stream(self, player_id):
        return self.query(player_id, "remote", "?")['_remote'] == 1

    def get_artist_album(self, player_id, artist_id):
        return self.query(player_id, "albums", 0, 99, "tags:al",
                          "artist_id:" + str(artist_id))['albums_loop']

    def get_alarms(self, player_id, enabled=True):
        if enabled:
            alarmsEnabled = self.get_player_pref(player_id, "alarmsEnabled")
            if alarmsEnabled == "0":
                return {}
            alarm_filter = "enabled"
        else:
            alarm_filter = "all"
        return self.query(player_id, "alarms", 0, 99,
            "filter:%s" % alarm_filter)

    def get_next_alarm(self, player_id):
        alarms = self.get_alarms(player_id)
        alarmtime = 0
        delta = 0
        if alarms == {} or alarms['count'] == 0:
            return {}
        for alarmitem in alarms['alarms_loop']:
            if(str((datetime.datetime.today().weekday() + 1) % 7)
               not in alarmitem['dow']):
                continue
            alarmtime_new = datetime.timedelta(seconds=int(alarmitem['time']))
            now = datetime.datetime.now()
            currenttime = datetime.timedelta(hours=now.hour,
                                             minutes=now.minute,
                                             seconds=now.second)
            delta_new = alarmtime_new - currenttime
            if delta == 0:
                delta = delta_new
                alarmtime = alarmtime_new
            elif delta_new < delta:
                delta = delta_new
                alarmtime = alarmtime_new
        if alarmtime == 0:
            return {}
        else:
            return {"alarmtime": alarmtime.seconds, "delta": delta.seconds}

    def get_player_pref(self, player_id, pref):
        return self.query(player_id, "playerpref", pref, "?")['_p2']

    def set_player_pref(self, player_id, pref, value):
        self.query(player_id, "playerpref", pref, value)

    def display(self, player_id, line1, line2, duration=5):
        self.query(player_id, "display", line1, line2, duration)

    def display_all(self, line1, line2, duration=5):
        players = self.get_players()
        for player in players:
            self.display(player['playerid'], line1, line2, duration)


