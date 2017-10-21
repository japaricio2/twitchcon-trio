'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import sys
import irc.bot
import requests

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        #twitter INIT
        consumer_key = 'mj9lFkDA55M8yRfXRotDfiEt6'
        consumer_secret = 'WxVCkxLyDKIFgRW1Jm1TRf3Q7Ec7WS4Or7iSBOf8Fo9Pj4GvE8'
        access_token_key = '239036830-2NL2MhgnUZo69LRU2SLUECGgrH16EFgXSp9woUIU'
        access_token_secret = 'I3aEJSFGclBQgNupBpFF9zO6H98wQnghtpgrF4SQxGvUJ'
        self.api = twitter.Api(
          consumer_key=consumer_key,
          consumer_secret=consumer_secret,
          access_token_key=access_token_key,
          access_token_secret=access_token_secret
        )
        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)
        

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(e, cmd)
        return

    def do_command(self, e, cmd):
        c = self.connection
        # Poll Twitter Api for last tweet (hardcode)
        if cmd=="tweet":
            latest_tweet = self.api.GetUserTimeline(screen_name='aspceo')
            c.privmsg(self.channel, latest_tweet[0].text)

        # Poll the API to get current game.
        elif cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])

        # Poll the API the get the current status of the stream
        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])

        # Provide basic information to viewers for specific commands
        elif cmd == "raffle":
            message = "This is an example bot, replace this text with your raffle text."
            c.privmsg(self.channel, message)
        elif cmd == "schedule":
            message = "This is an example bot, replace this text with your schedule text."            
            c.privmsg(self.channel, message)
        elif cmd == "spotify_current":
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
        else:
            c.privmsg(self.channel, "Did not understand command: " + cmd)

def main():
    if len(sys.argv) != 5:
        print("Usage: twitchbot <username> <client id> <token> <channel>")
        sys.exit(1)

    username  = sys.argv[1]
    client_id = sys.argv[2]
    token     = sys.argv[3]
    channel   = sys.argv[4]

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()