import base_game
import threading
import twitch_api


class EmoteGuessGame(base_game.BaseGame):

    db = ''

    def __init__(self, irc):
        time = 60  # in seconds
        choices = twitch_api.get_all_emotes(irc.channel)
        super().__init__(choices, time, irc)

    async def game_command(self, arg, userid):
        print('userid: ' + str(userid) + ' channelid: ' + str(twitch_api.get_id_from_username(self.irc.channel)))
        if int(userid) == int(twitch_api.get_id_from_username(self.irc.channel)):
            if arg[0] == 'start':  # command argument was start to initiate a game
                print('start')
                if arg[1] in self.choices:
                    print('arg is choices')
                    self.answer = arg[1]
                    await self.start_game('Emote guessing game has started! '
                                          'you have a minute to guess the right answer!')

    async def check_answer(self, answer, username, db, chat):
        if answer.find(' ') == -1:
            if await super().check_answer(answer, username, db, chat) is True:
                self.timer.cancel()  # if answer was right cancel the timer and end the game

    async def start_game(self, opening_msg):
        self.timer = threading.Timer(float(self.game_time),
                                     self.timed_method)  # ,[self.irc]
        self.on_going = True
        await super().start_game(opening_msg)  # generate base object
        self.timer.start()  # start the timeout timer
