import json
import requests
import http.server
import socketserver
import webbrowser
import urllib.parse
import base64


REDIRECT_URI = "http://localhost:8080"
SCOPES = "chat:read+chat:edit"
PORT = 8080


def updatekeys(jsoninput):
    with open("keys.json", "w+") as f:
        json.dump(jsoninput, f, indent=2)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" in params:
                code = params["code"][0]
            if "state" in params:
                state = params["state"][0]

            with open("keys.json", 'r+') as j:
                keysfilejson = json.load(j)



            if state == "twitch":
                url = "https://id.twitch.tv/oauth2/token"
                data = {
                        "client_id": keysfilejson[state]["id"],
                        "client_secret": keysfilejson[state]["secret"],
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": REDIRECT_URI
                    }
                headers = {}#make sure this works

            elif state == "spotify":
                url = "https://accounts.spotify.com/api/token"
                data = {
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": REDIRECT_URI
                    }
                headers = {
                        "content_type": "application/x-www-form-urlencoded",
                        "Authorization": f"Basic {base64.b64encode(f"{keysfilejson[state]["id"]}:{keysfilejson[state]["secret"]}".encode()).decode()}"
                    }
            else:
                raise LookupError.add_note("State returned doesn't match one of the possibilties")
            #add additional http handlers above


            
            try:
                resp = requests.post(url, data = data, headers = headers)
                resp.raise_for_status()
            
            except http.HTTPError as e:
                self.send_response(resp.status_code)
                print(f"Error connecting to {state} with code {resp.status_code}")
            
            keys = resp.json()
            keysfilejson[state]["access"] = keys["access_token"]
            keysfilejson[state]["refresh"] = keys["refresh_token"]
            

            updatekeys(keysfilejson)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Auth complete. You can close this window.")





def auth():
    with open("keys.json", 'r+') as j:
        tokens = json.load(j)
        j.close()
        twitch_url = (
            "https://id.twitch.tv/oauth2/authorize"
            f"?client_id={tokens["twitch"]["id"]}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            f"&scope={SCOPES}"
            f"&state=twitch"
        )

        spotify_url = (
            "https://accounts.spotify.com/authorize"
            f"?client_id={tokens["spotify"]["id"]}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=app-remote-control"
            f"&state=spotify"
        )
        
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("Opening browser for Twitch authentication...")
            webbrowser.open(twitch_url)
            httpd.handle_request()
            webbrowser.open(spotify_url)
            httpd.handle_request()
            print("Completed")

            
        
if __name__ == "__main__":
    auth()