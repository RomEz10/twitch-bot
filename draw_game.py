import random
import threading
# when first starts should pick a word from a list of objects to draw and start a timer
# when either time ends or word is guesses correctly the game should end


class DrawGame:

    on_going = False
    how_long = 0
    choices = ['computer', 'camel', 'cup']
    draw = ''
    draw_timer = ''

    def draw_command(self, arg, username, irc, db, chat):
        if arg == 'wins':
            irc.send(irc.channel, username + ', you have ' + str(db.get_guesses(db, chat)) + ' wins')
        else:
            if self.on_going is True:  # if a game is currently running
                if self.answer(arg, username, irc, db, chat) is True:
                    self.draw_timer.cancel()  # if answer was right cancel the timer and end the game
            else:
                if arg == 'start':  # command argument was start to initiate a game
                    self.draw_timer = threading.Timer(60.0,
                                                      self.timer)
                    self.on_going = True
                    self.start_game(irc)  # generate draw object
                    self.draw_timer.start()  # start the timeout timer
        print(self.on_going)
        return 'draw'

    def start_game(self, irc):  # start the game and pick a random object to draw
        self.draw = random.choice(self.choices)
        irc.send_whisper(irc.channel, irc.channel, 'you should draw ' + self.draw)
        irc.send(irc.channel, 'Drawing game has started! you have a minute to guess the right answer!')

    def answer(self, answer, username, irc, db, chat):  # check answer, if true stop the game
        if answer == self.draw:
            self.on_going = False
            irc.send(irc.channel, username + ' got the answer right!')
            db.add_points(db, chat, 5)
            db.add_guesses(db, chat)
            return True
        else:
            print('incorrect guess.')
            return False

    def timer(self):  # if time runs out- stop the game
        print('time ran out')
        self.on_going = False
