import base_game
import twitch_api
import random
import asyncio


class FactionsGame(base_game.BaseGame):

    prep_timer = 30  # time in seconds. this is how long players can join the game.
    start_delay = 5  # time in seconds. this is how long the delay between the last whisper sent and the start of game.
    game_timer = 60  # time in seconds. this is how long the spam portion of the game is.
    win_points = 2  # INT. number of points gained per win.
    min_factions = 2  # INT. minimum number of factions.
    max_factions = 4  # INT. maximum number of factions.
    participants = []
    teams = {}
    prep_time = False

    def __init__(self, irc, db):
        time = 60
        super().__init__([], time, irc)
        self.db = db
        self.choices = {}

    async def game_command(self, arg, username, db, chat):
        # before starting a game we need to make sure faction emotes are correct and the max factions value fits the
        # value in the global var.
        # starting faction game by: !faction <emote> <emote> <emote> ...
        # amount of emotes typed in the faction command must be withing or equal to min_factions and max_factions range.
        # after starting each chatter has to whisper !join to the bot before time runs out (value of prep_timer).
        # after the time has passed the bot assigns everyone a team and whispers them back their team
        # game starts after the time of start_delay passes and lasts for the value of game_timer
        # each participant should spam his team's emote, each message containing the emote counts as 1
        # when the game ends the team who spammed the emote the most wins, value of win_points is added to their points
        if chat.name == self.irc.channel:
            if self.on_going is False and self.prep_time is False:
                emotes = twitch_api.get_all_emotes(username)
                if self.min_factions-1 < len(arg) <= self.max_factions:
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
                        self.reset_game()
                else:
                    await self.irc.send(username, 'Maximum amount of factions allowed are ' + str(self.max_factions) +
                                        ' and the minimum is ' + str(self.min_factions))

    async def start_registration(self):
        # waiting for everyone to register with a whisper, calling join_game()
        await asyncio.sleep(self.prep_timer)
        await self.timed_method()

    async def faction_emote(self, emotes, chatter):
        # getting all of the emotes used in a message, if they match one of the factions count it
        emotes = list(dict.fromkeys(emotes))  # removing duplicates
        for emote in emotes:
            if emote in self.choices.keys() and chatter.twitch_id in self.teams[emote]:
                self.choices[emote] += 1

    async def start_game(self, opening_msg):
        # starting the game, after the time passes ending it
        self.on_going = True
        await self.irc.send(self.irc.channel, opening_msg)
        await asyncio.sleep(self.game_timer)
        await self.end_game()

    async def end_game(self):
        # ending the game, finding out the winner, giving away points and resetting.
        if self.on_going is True:
            most_spammed_emotes = 0
            for choice in self.choices.items():
                # choice is a tuple (k,v)
                if not most_spammed_emotes or choice[1] > most_spammed_emotes[1]:
                    most_spammed_emotes = choice
            print('score: ' + str(self.choices))
            await self.irc.send(self.irc.channel, 'The game has ended, winner team is ' + most_spammed_emotes[0])
            self.db.add_points_bulk(self.db, self.teams[most_spammed_emotes[0]], self.win_points)
        self.reset_game()

    async def timed_method(self):
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
            await self.assign_teams()
        else:
            await self.irc.send(self.irc.channel, 'Not enough people joined the game.')
            self.reset_game()
            # cancel game

    async def join_game(self, twitch_id):
        # getting called from the pubsub client only if prep_time is True
        self.participants.append(twitch_id)

    async def assign_teams(self):
        # after prep_time has ended this func assigns everyone a team and notifies them, game is starting after that.
        teams = self.teams
        msgs, targets = [], []
        for faction in teams:
            for player in teams[faction]:
                msgs.append('Your team is ' + faction)
                targets.append(player)
        await self.irc.send_whisper_bulk(self.irc.channel, msgs, targets=targets)
        msgs = ['All participants have received a whisper with their team, if you didn\'t '
                'receive a whisper please send me a friend request and retry next game',
                'The game will start in ' + str(self.start_delay) + ' seconds']
        await self.irc.send_bulk(self.irc.channel, msgs)
        await asyncio.sleep(self.start_delay)
        self.prep_time = False  # Game is starting, prep time is over
        await self.start_game('Teams are assigned. Please spammerino in the chatterino!')

    def reset_game(self):
        self.participants = []
        self.teams = {}
        self.choices = {}
        self.prep_time = False
        self.on_going = False

