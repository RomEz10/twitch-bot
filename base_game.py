import threading
import asyncio


class BaseGame:

    on_going = False
    how_long = 0
    choices = ['computer', 'camel', 'cup']
    answer = ''
    timer = threading.Timer
    irc = ''

    def __init__(self, choices, game_time, irc):
        self.choices = choices
        self.game_time = game_time
        self.irc = irc

    async def generic_game_command(self, arg, username, db, chat):
        print('override me')

    async def start_game(self, opening_msg):  # start the game and pick a random object to draw
        await self.irc.send(self.irc.channel, opening_msg)

    async def check_answer(self, answer, username, db, chat):  # check answer, if true stop the game
        print('answer: ' + answer + ' self answer: ' + self.answer)
        if answer == self.answer:
            self.on_going = False
            await self.irc.send(self.irc.channel, username + ' got the answer right!')
            db.add_points(db, chat, 5)
            db.add_guesses(db, chat)
            return True
        else:
            print('incorrect guess.')
            return False

    def timed_method(self):  # if time runs out- stop the game
        print('time ran out')
        asyncio.new_event_loop().run_until_complete(self.irc.send(self.irc.channel,
                                                                  self.answer + ' but time ran out!'))
        self.on_going = False
