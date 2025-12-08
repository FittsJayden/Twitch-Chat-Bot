This is a very simple python Twitch Chat-to-Spotify program that uses the Twitch API to read your chatroom, parse through the text sent, and look for key commands that can engage specific features of the bot. At the moment, the only feature working is the add-to-queue feature. It has no UI, and is controlled through the python command line.

How to use:

1. Create developer apps on both Spotify and Twitch. This can be done by going to both devloper websites i.e. https://dev.twitch.tv/ & https://developer.spotify.com/dashboard/login . Once these extensions or applications are created on their end, now you must input the app client ids into the code itself. (This can be done in any text editor or IDE, just make sure it is saved as a .py when you are done)

twitch_id= "Twitch app id here"
twitch_secret= "Twitch app secret token here"

CLIENT_ID= "Spotify app id here"
CLIENT_PASS= "Spotify app secret token here"


2. Now input the rest of the information according to your spotify and twitch account respectively.

CHANNEL= #"Twitch channel username" (make sure you include the "#" before the username)

username= "Spotify username"


3. Now get your oauth for Twitch by going here: https://twitchapps.com/tmi/ and following the instructions. It should look something like this: oauth:************************. Now input this into the code,

PASS= "entire oauth token goes here"


4. Everything should be ready to go! Now we hvae to install python and the libraries we'll be using if they aren't already on your machine. The simplest way is to go to the windows store and search "python" and it should pop up. Click install.


5. Now that we have python, open up your command prompt, and type "pip install spotipy" and hit enter. Do the samething with "pip install pyttsx3". The rest of the libraries are packaged with python.


6. Now simply double click on the program and it will run. It may launch your default browser and ask you to log into Spotify, this is for Spotipy. It allows the users information to be saved locally and kept so you don't have to login everytime.
