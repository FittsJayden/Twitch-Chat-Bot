import asyncio
import re
import threading
import json
import time
import websockets
import requests
from filelock import FileLock

PRIVMSG_RE = re.compile(r"^(?:@(?P<tags>[^\s]+) )?:(?P<prefix>[^ ]+) PRIVMSG #(?P<channel>[^ ]+) :(?P<message>.*)$")
NOTICE_RE = re.compile(r"^:(?P<host>[^ ]+) NOTICE \* :(?P<notice>.*)$")

class TwitchWebSocketBot:
    def __init__(self, key_path, bot_username, channel, reconnect=True):

        self.loop = None
        self.key_path = key_path
        self.username = bot_username.lower()
        self.channel = channel.lower()
        self.server = "wss://irc-ws.chat.twitch.tv:443"
        self.commands = {}
        self.running = False
        self.reconnect = reconnect
        self._ws = None
        self.section = "twitch"

        with open(self.key_path, "r") as f:
            keys = json.load(f)["twitch"]

        self.access = "oauth:" + keys["access"]
        self.refresh = keys["refresh"]
        self.id = keys["id"]
        self.secret = keys["secret"]
            

    def _token_refresh(self):
        resp = requests.post("https://id.twitch.tv/oauth2/token", data = {
                "client_id": self.id,
                "client_secret": self.secret,
                "grant_type": "authorization_code",
                "refresh_token": self.refresh
            }, headers = {
                "content_type": "application/x-www-form-urlencoded"
                })
        
        self.access = resp.json()["access_token"]
        self.refresh = resp.json()["refresh_token"]

        with FileLock(self.key_path + ".lock"):
            with open(self.key_path, "r") as f:
                data = json.load(f)
            data[self.section]["access"] = self.access
            data[self.section]["refresh"] = self.refresh
            with open(self.key_path, "w") as f:
                json.dump(data, f, indent=2)




    def register_command(self, keyword, func):
        self.commands[keyword.lower()] = func

    async def _authenticate_and_join(self, ws):
        await ws.send("CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership")
        
        await ws.send(f"PASS {self.access}")
        await ws.send(f"NICK {self.username}")
        await ws.send(f"JOIN #{self.channel}")

    def _parse_tags(self, raw_tags):
        tags = {}
        if not raw_tags:
            return tags
        for item in raw_tags.split(";"):
            if "=" in item:
                k, v = item.split("=", 1)
                tags[k] = v
            else:
                tags[item] = ""
        return tags

    async def _dispatch(self, user, message, tags):
        low = message.lower()
        for key, func in self.commands.items():
            if key in low:
                message = message.replace(key, "").strip()
                self.say(await asyncio.to_thread(func, self, user, message, tags))


    async def _handle_ws_message(self, text, ws):
        if text.startswith("PING"):
            await ws.send("PONG :tmi.twitch.tv")
            return

        m_notice = NOTICE_RE.match(text)
        if m_notice:
            notice = m_notice.group("notice") or ""
            print("NOTICE:", notice)
            if "Login authentication failed" in notice or "Improperly formatted auth" in notice:
                print("Auth failed — check token or refresh it.")
                self._token_refresh()
            return

        # PRIVMSG parsing
        m = PRIVMSG_RE.match(text)
        if not m:
            return

        raw_tags = m.group("tags")
        prefix = m.group("prefix")
        message = m.group("message")
        tags = self._parse_tags(raw_tags)

        user = tags.get("display-name")
        if not user:
            user = prefix.split("!", 1)[0].lstrip(":")

        print(f"{user}: {message}")
        asyncio.run_coroutine_threadsafe(self._dispatch(user, message, tags), self.loop)


    async def _run_loop(self):
        self.loop = asyncio.get_running_loop()
        backoff = 1
        while True:
            try:
                async with websockets.connect(self.server) as ws:
                    self._ws = ws
                    await self._authenticate_and_join(ws)
                    print("Connected and joined", self.channel)
                    backoff = 1
                    async for raw in ws:
                        await self._handle_ws_message(raw, ws)
            except Exception as exc:
                print("WebSocket error:", exc)
                if not self.reconnect or not self.running:
                    break
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
                print(f"Reconnecting (backoff {backoff}s)...")
            finally:
                self._ws = None
            if not self.reconnect or not self.running:
                break

    def run(self):
        self.running = True
        asyncio.run(self._run_loop())

    def stop(self):
        self.running = False
        print("Stopping bot...")

    def say(self, text):
        """Send a message to chat. Can be called from other threads.
        Note: this schedules an async send using asyncio.run_coroutine_threadsafe if loop exists.
        """
        # If the websocket is open, send (async). If not, ignore or return False.
        if not self._ws:
            print("Can't send message — websocket not connected.")
            return False

        async def _send():
            await self._ws.send(f"PRIVMSG #{self.channel} :{text}")

        # get running loop and schedule
        loop = asyncio.get_event_loop()
        try:
            # If running inside asyncio loop, schedule; otherwise run in background
            asyncio.run_coroutine_threadsafe(_send(), loop)
            return True
        except RuntimeError:
            # no running loop in this thread — spawn a small helper
            asyncio.run(_send())
            return True
