'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import cfg
import sys
import irc.bot
import requests

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, token)], username, username)

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        # If a chat message starts with an exclamation point, try to run it as a command
        # print(e.arguments[0])
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(e, cmd)
        elif 'gonna' in e.arguments[0]:
            cmd = 'gonna'
            #print(cmd)
            self.insideJoke(e, cmd)
        elif 'going' in e.arguments[0]:
            cmd = 'going'
            #print(cmd)
            self.insideJoke(e, cmd)
        return

    def insideJoke(self, e, cmd):
        c = self.connection
        c.privmsg(self.channel, "bet you won't.")

    def do_command(self, e, cmd):
        c = self.connection
        # Poll the API to get current game.
        if cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            if r['game'] is None:
                c.privmsg(self.channel, "There is no game currently being played.")
            else:
                c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])

        # Poll the API the get the current status of the stream
        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])

        # provides streamer schedule
        elif cmd == "schedule":
            sched = ['Monday: 12PM - 8PM', 'Tuesday: 4PM - 7PM', 'Wednesday: 12PM - 5PM', 'Thursday: OFF', 'Friday: 10AM - 2PM', ]
            for i in sched:
                c.privmsg(self.channel, i)

        # favorite artist
        elif cmd == "fav_artist":
            # make request to spotify api
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            display_name = (r['display_name'])
            # print("DISPLAY " + display_name)
            spot_url = 'https://api.spotify.com/v1/me/top/artists?limit=5'
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer BQC9TDED6Er5JOftJyFPliUVFHjlbrdfrfVLqyRoI8kIseYjxcGw047Ms6vD1IB9nenRXp9TwAEB6ZOTqf7dhNb1zITnDTo9N0AJTMeDHlBCWqDXw8aBqxc3a7lTw4l8Nv7CnPmYr20cVsHDDnc',
            }
            rr = requests.get(spot_url, headers=headers).json()
            artist = rr['items'][0]['name']
            message = display_name + ' favorite artist is ' + artist
            c.privmsg(self.channel, message)

        # get song that is now playing
        elif cmd == 'playing':
            spot_url = 'https://api.spotify.com/v1/me/player/currently-playing'
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer BQBuI97W8oZQRykDe_n_oD2ND1l5MlgtEbBPT__nxtQYmxRBatbydIMX51PqTG8bRQDC4iCu1p39qtkHzQn6iV5EEuaBasNNXjIU5dVJKHQGrJGi-KRLWIkvfslHJZuzN6RN9YHXzhQLcin__dcJ3VUMcza09A',
            }
            r = requests.get(spot_url, headers=headers).json()
            #print(r)
            song = r['item']['name']
            artist = r['item']['artists'][0]['name']
            if r['is_playing'] == True and r['context']['type'] == 'playlist':
                c.privmsg(self.channel, song + ' - ' + artist + ' is now playing from: ' + r['context']['external_urls']['spotify'])
            elif r['is_playing'] == True:
                c.privmsg(self.channel, song + ' - ' + artist + ' is now playing')
            else:
                c.privmsg(self.channel, 'There is nothing currently being played.')

        else:
            c.privmsg(self.channel, "Did not understand command: " + cmd)

def main():
    bot = TwitchBot(cfg.username, cfg.client_id, cfg.token, cfg.channel)
    bot.start()

if __name__ == "__main__":
    main()
