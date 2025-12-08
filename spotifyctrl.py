import requests
import json
import base64
from filelock import FileLock
import re
import startup
import bot

class SpotifyControl:
    def __init__(self, key_path):
        self.key_path = key_path
        self.section = "spotify"

        with open(key_path, "r") as f:
            self.keys = json.load(f)["spotify"]
    
    def refresh_token(self):
        resp = requests.post("https://accounts.spotify.com/api/token", data={
            "grant_type": "refresh_token",
            "refresh_token": self.keys["refresh"]
        }, headers ={
            "content_type": "application/x-www-form-urlencoded",
            "authorization": f"Basic {base64.b64encode(f"{self.keys["id"]}:{self.keys["secret"]}".encode()).decode()}"
        })

        self.keys["access"] = resp.json()["access_token"]

        with FileLock(self.key_path + ".lock"):
            with open(self.key_path, "r") as f:
                data = json.load(f)
            data[self.section]["access"] = self.keys["access"]
            with open(self.key_path, "w") as f:
                json.dump(data, f, indent=2)
    
    def song_search(self, string):
        if ".com" in string.lower():
            match = re.search(r"track/([A-Za-z0-9]+)", string)
            if not match:
                raise ValueError("Not a valid Spotify track URL.")
            track_id = match.group(1)

            for attempt in range(2):
                r = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=
                                {"Authorization": f"Bearer {self.keys["access"]}"
                })
                if r.status_code == 401:
                    self.refresh_token()
                    continue
                else:
                    break
            r.raise_for_status()
            
            return r.json()["uri"], track_id
        
        else:
            for attempt in range(2):
                r = requests.get(f"https://api.spotify.com/v1/search", params={
                    "q": f"track:{string}",
                    "type":"track",
                    "limit": 1
                }, headers= {
                    "Authorization": f"Bearer {self.keys["access"]}"
                })


                if r.status_code == 401:
                    self.refresh_token()
                    continue
                else:
                    break

            r.raise_for_status()
                
            return r.json()["tracks"]["items"][0]["uri"], r.json()["tracks"]["items"][0]["id"]#items is an array
        
    def add_to_queue(self, bot, user, string, tags):
        
        try:
            uri, track_id = self.song_search(string)
        except Exception:
            return ("That URL/song name didn't work...")

        for attempt in range(2):
            r = requests.post(f"https://api.spotify.com/v1/me/player/queue", headers={
                "Authorization": f"Bearer {self.keys["access"]}"
                }, params={
                "uri": uri
            })
            #get song name
            r2 = requests.get(f"https://api.spotify.com/v1/tracks", headers={
                "Authorization": f"Bearer {self.keys["access"]}"
                }, params={
                "ids": re.search(r"track:([A-Za-z0-9]+)", uri).group(1)
            })

            if r.status_code == 401 or r2.status_code == 401:
                self.refresh_token()
                continue
        try:
            r.raise_for_status()
            r2.raise_for_status()
        except Exception as e:
            return ("He's not playing music rn, can't queue...")

        return f"Queued {r2.json()["tracks"][0]["name"]} by {r2.json()["tracks"][0]["artists"][0]["name"]}"



if __name__ == '__main__':
    startup.auth()
    spotify = SpotifyControl("keys.json")
    spotify.add_to_queue("https://open.spotify.com/track/60zIis3BtyfNQFEucmDvE7?si=0ababd1a0c384388")