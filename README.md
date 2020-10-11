# twitch-games-bot

twitch-games-bot is a Python script that act as a chat bot on [twitch.tv](https://twitch.tv/)

## Requirements

Currently the following external packages are required to run this chat bot:


[sqlAlchemy](https://www.sqlalchemy.org) - handles database very easily for sql noobs

[requests](https://2.python-requests.org/en/master) - handles http get + post, also provides easy conversion to JSON.

[websockets](https://websockets.readthedocs.io) - easy websocket implementation currently implemented in [whispers.py](https://github.com/RomEz10/twitch-bot/blob/master/whispers.py)

access oauth token with 'whispers:read' scope, refer to to the [wiki](https://github.com/RomEz10/twitch-bot/wiki) if you don't know how to get one

## Usage
If you want to run this bot please follow the tutorial in the [wiki](https://github.com/RomEz10/twitch-bot/wiki)

## Games
### Draw
Bot picks an object for streamer to draw, first chatter that guesses right wins.
### Emote guesses
Streamer whispers bot with an emote and chat has to guess, bttv/ffz supported.
### Factions
Everyone in chat is being sorted into factions based on emotes chosen by the streamer, chatters get whispers in which faction they are. The most spammed emote wins (each message containing the emote(s) is count as 1)
### Court-house - an idea
Streamer picks judges, defendant and two lawyers. They both have time to make arguments. Jury (chat) then decides if chatter should be banned.



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0)
