import startup
import bot
import spotifyctrl
import functions
import blackjack
import database

#DB_PATH= "currency.db"
KEYS_PATH = "keys.json"
CHANNEL_NAME = "sttifs" #PUT CHANNEL NAME HERE!

if __name__ == '__main__':
    
    startup.auth()
    db = database.CurrencyDB(DB_PATH)
    blackjack.BlackJackBot(db)

    spotifyob = spotifyctrl.SpotifyControl(KEYS_PATH)
    tbot = bot.TwitchWebSocketBot(KEYS_PATH, CHANNEL_NAME ,CHANNEL_NAME)

    tbot.register_command("!sr", spotifyob.add_to_queue)

    tbot.run()
