import socket
import time
import spotipy
import spotipy.util as util
import pyttsx3
import sys
from random import randint
import re


#twitch information
HOST = 'irc.chat.twitch.tv'
twitch_id = '**************************'
twitch_secret = '***************************'
PORT = 6667
NICK = 'SttifsBot'
#The PASS string must contain an oauth code for your twitch account. That can be retreived here: https://twitchapps.com/tmi/
PASS = 'oauth:***************************'
CHANNEL = '#sttifs'

#spotify information
username = 'fittsjayden'
CLIENT_ID = '0245db36b1924b288d4785188422affd'
CLIENT_SECRET = 'badd729f2f484de097dac2bcee36da79'
redirect_uri = 'http://127.0.0.1:8000'
scope = 'user-modify-playback-state'
token = util.prompt_for_user_token(username, scope, CLIENT_ID, CLIENT_SECRET, redirect_uri)
sp = spotipy.Spotify(auth=token)
engine = pyttsx3.init()
engine.setProperty('volume',0.6)





startident = 1

endcode = str(randint(100000, 999999))
print('Type "', endcode,'" into chat to stop the bot.')

def send_message(msg,s):
    s.send(bytes("PRIVMSG " + CHANNEL + " :" + msg + "\r\n", "UTF-8"))

def spotifyscan(message, username, s):
    print(username, message)
    cmd, song = message.split(' ', 1)
    result = sp.search(song, type='track', limit=1)
    try:
        trackId = result['tracks']['items'][0]['id']
    except IndexError:
        send_message('Spotify couldn\'t find that song, make sure it\'s available there! If you put a link, try the song name instead, song links don\'t work yet.', s)
        return
    sp.add_to_queue(trackId)
    artist = result['tracks']['items'][0]['artists'][0]['name']
    trackname = result['tracks']['items'][0] ['name']
    full = '{} queued | {} by {} |'.format(username.capitalize(), trackname, artist)
    send_message(full, s)

def start():
    print("Connecting to host!")
    s = socket.socket()
    s.connect((HOST, PORT))
    s.send(bytes("PASS " + PASS + "\r\n", "UTF-8"))
    s.send(bytes("NICK " + NICK + "\r\n", "UTF-8"))
    s.send(bytes("JOIN %s\r\n" % CHANNEL, "UTF-8"))
    print("Connected to host!")
    send_message("Connected to "+CHANNEL[1:]+'\'s chat!', s)
    return s
    
def readchat(s):
        while True:
            for line in str(s.recv(1024)).split('\r\n'):
                if "PING :tmi.twitch.tv" in line:
                    print("PONG :tmi.twitch.tv")
                    s.send(bytes("PONG :tmi.twitch.tv\r\n", "UTF-8"))
            parts = line.split(':')
            if len(parts) < 3:
                continue
            message = parts[2][:len(parts[2])]
            message = message.strip("")
            message = message[:(len(message) - 5)]
            usernamesplit = parts[1].split("!")
            username = usernamesplit[0]
            regex = re.compile('[,\.?]')
            regex.sub('', message)
            
            print(time.strftime("%H:%M:%S"), username + ": " + message)
            if message.startswith('!sr ') or message.startswith('!SR ') or message.startswith('!Sr ') or message.startswith('!sR '):
                spotifyscan(message, username, s) 
            if message.startswith('!g ') or message.startswith('!G '):
                 gamble(message, username, s)
            elif message.startswith('Welcome, GLHF!') or message.startswith('sttifs.tmi.twitch.tv') or username.startswith('nightbot') or username.startswith('streamelements') or message.startswith('<3'):
                None
            elif message.startswith(endcode):
                sys.exit()
            else:
                break
        ttschat(message,s)


        
def ttschat(message,s):
    engine.say(message)
    engine.runAndWait()
    
while True:
    if startident == 1:
        startident = 0
        s = start()
    else:
        readchat(s)