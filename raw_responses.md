# Raw responses- 
This file includes some raw responses as string straight from twitch/ third party without any parsing in hopes of it helping me/others in the future.
The responsed are mostly received in [twitch_api.py](https://github.com/RomEz10/twitch-bot/blob/master/twitch_api.py)

Make sure you view this file in markdown reader, reading the file as simple text file will include escaping characters which doesn't reflect the actual response.

Unless stated otherwise <> refers to output that depends on your implementation/ specific run

### Successful irc connection should look like this:

:tmi.twitch.tv 001 \<username> :Welcome, GLHF!\r\n
  
:tmi.twitch.tv 002 \<username> :Your host is tmi.twitch.tv\r\n
  
:tmi.twitch.tv 003 \<username> :This server is rather new\r\n
  
:tmi.twitch.tv 004 \<username> :-\r\n
  
:tmi.twitch.tv 375 \<username> :-\r\n
  
:tmi.twitch.tv 372 \<username> :You are in a maze of twisty passages, all alike.\r\n
  
:tmi.twitch.tv 376 \<username> :>\r\n
  
:\<chatter>!\<botname>@\<channel>.tmi.twitch.tv JOIN #\<channel>\r\n
  
:\<channel>.tmi.twitch.tv 353 \<username> = #\<channel> :\<username>\r\n
  
:\<channel>.tmi.twitch.tv 366 \<username> #\<channel> :End of /NAMES list\r\n

### Simple irc message received

:\<chatter>!\<chatter>@\<chatter>.tmi.twitch.tv PRIVMSG #\<channel> :\<message>\r\n

### Simple irc message sent

PRIVMSG #\<channel> :\<message>\r\n

### Pubsub webhook client registration

{"type": "LISTEN", "data": {"topics": ["\<topic>.\<user_id>"], "auth_token": "\<auth_token>"}}

### Pubsub webhook start of session acknowledgment 

{"type":"RESPONSE","error":"","nonce":"\<random string to follow request>"}

### Pubsub action

for pubsub actions refer to the docs [here](https://dev.twitch.tv/docs/pubsub)

### Getting ffz channel emotes

an example response can be seen [here](https://api.frankerfacez.com/v1/room/m0xyy) for docs refer to [this](https://www.frankerfacez.com/developers) under "GET /room/id/:twitch_id or GET /room/:name"

### Getting ffz global emotes

an example response can be seen [here](https://api.frankerfacez.com/v1/set/global) for docs refer to [this](https://www.frankerfacez.com/developers) under "GET /set/global"

### Getting bttv channel emotes

an example response can be seen [here](https://api.betterttv.net/3/cached/users/twitch/69012069) (numbers in the url are twitch id) there are no official docs.

### Getting bttv global emotes

an example response can be seen [here](https://api.betterttv.net/3/cached/emotes/global) there are no official docs.
