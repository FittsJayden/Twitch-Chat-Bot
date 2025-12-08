This is a very simple python Twitch Chat-to-Spotify program that uses the Twitch API to read your chatroom, parse through the text sent, and look for key commands that can engage specific features of the bot. At the moment, the only feature working is the add-to-queue feature. It has no UI, and is controlled through the command line.

How to use:

1. Create developer apps on both Spotify and Twitch. This can be done by going to both devloper websites i.e. https://dev.twitch.tv/ & https://developer.spotify.com/dashboard/login . Once these extensions or applications are created on their end, now you must input the app client ids into keys.json.

2. Now input your twitch account name into main.py.

CHANNEL_NAME = "Twitch channel username" 


This was tested on Python 3.12. 
