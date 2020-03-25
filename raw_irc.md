# Raw IRC
This file includes some raw irc string received straight from twitch without any filtering in hopes of it helping me/others in the future.

## Successful connection should look like this:
:tmi.twitch.tv 001 <username> :Welcome, GLHF!
:tmi.twitch.tv 002 <username> :Your host is tmi.twitch.tv
:tmi.twitch.tv 003 <username> :This server is rather new
:tmi.twitch.tv 004 <username> :-
:tmi.twitch.tv 375 <username> :-
:tmi.twitch.tv 372 <username> :You are in a maze of twisty passages, all alike.
:tmi.twitch.tv 376 <username> :>
:<chatter>!<botname>@<channel>.tmi.twitch.tv JOIN #<channel>
:<channel>.tmi.twitch.tv 353 <username> = #<channel> :<username>
:<channel>.tmi.twitch.tv 366 <username> #<channel> :End of /NAMES list

:<chatter>!<botname>@<channel>.tmi.twitch.tv PRIVMSG #<channel> :<message>
