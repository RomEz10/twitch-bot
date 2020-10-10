import base_game
import twitch_api
import threading
import random
import asyncio
import chatter


class FactionsGame(base_game.BaseGame):

    participants = []
    teams = {}
    prep_time = False
    db = ''

    def __init__(self, irc, ):
        time = 60
        super().__init__([], time, irc)
        self.choices = {}

    async def game_command(self, arg, username, db, chat):
        print('game command faction')
        # before starting a game we need to make sure faction emotes are correct and there are max 4 factions
        # starting faction game by: !faction <emote> <emote> <emote> <emote>
        # after starting each chatter has a minute to whisper !join to the bot
        # after the minute passes the bot assigns everyone a team and whispers them their team back
        # game starts after 30 seconds and lasts for a minute
        # each participant should spam his team's emote, each message containing the emote counts as 1
        print('in game command')
        self.db = db
        if chat.name == self.irc.channel:
            if self.on_going is False and self.prep_time is False:
                emotes = twitch_api.get_all_emotes(username)
                if 1 < len(arg) <= 4:
                    # maximum factions allowed are 4 minimum are 2
                    for faction in arg:
                        # checking which factions streamer wants
                        if faction in emotes:
                            self.choices[faction] = 0
                            self.teams[faction] = []
                        else:
                            # break if a faction is not a usable emote
                            break
                    if len(arg) == len(self.choices):
                        await self.irc.send(self.irc.channel, 'Factions game is starting, you have a minute to join. '
                                                              'Whisper me !join')
                        await self.irc.send(self.irc.channel, 'In this game you\'re assigned a team, the team who '
                                                              'spams its emote the most wins.')
                        self.prep_time = True
                        await self.start_registration()
                        # start timer where people join via whispers
                    else:
                        # if not all the emotes match channel emotes
                        await self.irc.send(username, 'Please make sure you\'ve typed all the emotes correctly')
                else:
                    await self.irc.send(username, 'Maximum amount of factions allowed are 4')

    async def start_registration(self):
        self.timer = threading.Timer(60.0, self.timed_method).start()

    async def faction_emote(self, emotes, chatter):
        # getting all of the emotes used in a message, if they match one of the factions count it
        emotes = list(dict.fromkeys(emotes))  # removing duplicates
        for emote in emotes:
            if emote in self.choices.keys() and chatter.twitch_id in self.teams[emote]:
                self.choices[emote] += 1

    async def start_game(self, opening_msg):
        self.on_going = True
        await self.irc.send(self.irc.channel, opening_msg)
        self.timer = threading.Timer(60.0, self.end_game).start()

    def end_game(self):
        if self.on_going is True:
            self.on_going = False
            most_spammed_emotes = 0
            for choice in self.choices.items():
                # choice is a tuple (k,v)
                if not most_spammed_emotes or choice[1] > most_spammed_emotes[1]:
                    most_spammed_emotes = choice
            print('score: ' + str(self.choices))
            asyncio.new_event_loop().run_until_complete(
                self.irc.send(self.irc.channel, 'The game has ended, winner team is ' + most_spammed_emotes[0]))
            self.db.add_points_bulk(self.db, self.teams[most_spammed_emotes[0]], 2)

    def timed_method(self):
        print('in timed ' + str(self.participants) + ' ' + str(self.teams))
        # shuffling the participants list. after that assigning everyone to a team by going through each team and
        # assigning players to each team at a time, remainders are checked before and assigned in the same team loop.
        if len(self.participants) >= len(self.teams):
            random.shuffle(self.participants)
            player_count = int(len(self.participants) / len(self.teams))  # player count for each team
            player_remainder = len(self.participants) % len(self.teams)  # '%' operator returns the remainder
            for i, faction in enumerate(self.teams):
                # each faction gets a range
                self.teams[faction] = (self.participants[player_count*i:player_count*(i+1)])
                if player_remainder > 0:
                    self.teams[faction].append(self.participants[len(self.participants)-player_remainder])
                    # if we have remainder add one participant to this faction, list index is len-remainder
                    player_remainder -= 1
                    # reducing remainder till we hit 0, reducing the remainder will increase the index by 1 each loop
            asyncio.new_event_loop().run_until_complete(self.assign_teams())

        else:
            # TODO: remove run until complete and add something that doesnt blcok the thread
            asyncio.new_event_loop().run_until_complete(self.irc.send(self.irc.channel,
                                                                      'Not enough people joined the game.'))
            self.prep_time = False
            # cancel game

    async def join_game(self, twitch_id):
        self.participants.append(twitch_id)

    async def assign_teams(self):
        teams = self.teams
        msgs = [{'text': 'Your team is ' + faction, 'target': player} for faction in teams for player in
                teams[faction]]
        print(msgs)
        await self.irc.send_whisper_bulk(self.irc.channel, msgs)
        msgs = ['All participants have received a whisper with their team, if you didn\'t '
                'receive a whisper please send me a friend request and retry next game',
                'The game will start in 10 seconds']
        await self.irc.send_bulk(self.irc.channel, msgs)
        await asyncio.sleep(10)
        self.prep_time = False  # Game is starting, prep time is over
        await self.start_game('Teams are assigned please spammerino in the chatterino!')
