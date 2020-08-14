import random
import threading
import base_game
from offline_lists import nouns_list
# when first starts should pick a word from a list of objects to draw and start a timer
# when either time ends or word is guesses correctly the game should end


class DrawGame(base_game.BaseGame):
    def __init__(self, irc):
        time = 60
        choices = nouns_list
        super().__init__(choices, time, irc)

    async def game_command(self, arg, username, db, chat):
        if arg[0] == 'wins':
            await self.irc.send(self.irc.channel, username + ', you have ' +
                                str(db.get_guesses(db, chat)) + ' wins')
        else:
            if self.on_going is True:  # if a game is currently running
                if await self.check_answer(arg[0], username, db, chat) is True:
                    self.timer.cancel()  # if answer was right cancel the timer and end the game
            else:
                if arg[0] == 'start':  # command argument was start to initiate a game
                    await self.start_game('Drawing game has started! you have a minute to guess the right answer!')
        print(self.on_going)
        return 'draw'

    async def start_game(self, opening_msg):  # start the game and pick a random object to draw
        self.timer = threading.Timer(60.0,
                                     self.timed_method)
        self.on_going = True
        self.answer = random.choice(self.choices)
        await self.irc.send_whisper(self.irc.channel, self.irc.channel, 'you should draw '
                                    + self.answer)
        await super().start_game(opening_msg)
        self.timer.start()  # start the timeout timer


