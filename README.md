# twitch-games-bot

twitch-games-bot is a Python script that act as a chat bot on [twitch.tv](https://twitch.tv/)

## Requirements

Currently the following external packages are required to run this chat bot:


[sqlAlchemy](https://www.sqlalchemy.org) - handles database very easily for sql noobs

[requests](https://2.python-requests.org/en/master) - currently only used with http get with authorization header, also provides easy conversion to JSON.

## Usage
After downloading all of the required packages should clone this project and run [bot.py](https://github.com/RomEz10/twitch-bot/blob/master/bot.py)

## Games
### Draw
Bot picks an object for streamer to draw, first chatter that guesses right wins.
### Court-house - an idea
Streamer picks judges, defendant and two lawyers. They both have time to make arguments. Jury (chat) then decides if chatter should be banned.
### Factions - an idea
Everyone in chat is being sorted into factions based on popular emotes, chatters get whispers in which faction they are. The most spammed emote wins (each message containing the emote(s) is count as 1)


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0)
