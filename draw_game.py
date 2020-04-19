import random
import threading
import asyncio
# when first starts should pick a word from a list of objects to draw and start a timer
# when either time ends or word is guesses correctly the game should end


class DrawGame:

    on_going = False
    how_long = 0
    choices = ['computer', 'camel', 'cup']
    draw = ''
    draw_timer = ''

    async def draw_command(self, arg, username, irc, db, chat):
        if arg == 'wins':
            await irc.send(irc.channel, username + ', you have ' +
                           str(db.get_guesses(db, chat)) + ' wins')
        else:
            if self.on_going is True:  # if a game is currently running
                if await self.answer(arg, username, irc, db, chat) is True:
                    self.draw_timer.cancel()  # if answer was right cancel the timer and end the game
            else:
                if arg == 'start':  # command argument was start to initiate a game
                    self.draw_timer = threading.Timer(60.0,
                                                      self.timer, [irc])
                    self.on_going = True
                    await self.start_game(irc)  # generate draw object
                    self.draw_timer.start()  # start the timeout timer
        print(self.on_going)
        return 'draw'

    async def start_game(self, irc):  # start the game and pick a random object to draw
        self.draw = random.choice(self.choices)
        await irc.send_whisper(irc.channel, irc.channel, 'you should draw '
                               + self.draw)
        await irc.send(irc.channel, 'Drawing game has started! you have a minute to guess the right answer!')

    async def answer(self, answer, username, irc, db, chat):  # check answer, if true stop the game
        if answer == self.draw:
            self.on_going = False
            await irc.send(irc.channel, username + ' got the answer right!')
            db.add_points(db, chat, 5)
            db.add_guesses(db, chat)
            return True
        else:
            print('incorrect guess.')
            return False

    def timer(self, irc):  # if time runs out- stop the game
        print('time ran out')
        asyncio.new_event_loop().run_until_complete(irc.send(irc.channel, 'The answer was ' +
                                                             self.draw + ' but time ran out!'))
        self.on_going = False
