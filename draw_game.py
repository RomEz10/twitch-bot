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

    def draw_command(self, arg):
        if self.on_going is True:  # if a game is currently running
            if self.answer(arg) is True:
                self.draw_timer.cancel()  # if answer was right cancel the timer and end the game
        else:
            if arg == 'start':  # command argument was start to initiate a game
                self.draw_timer = threading.Timer(30.0,
                                                  self.timer)
                self.on_going = True
                self.start_game()  # generate draw object
                self.draw_timer.start()  # start the timeout timer
        print(self.on_going)
        return 'draw'

    def start_game(self):  # start the game and pick a random object to draw
        self.draw = random.choice(self.choices)
        print('you should draw ' + self.draw)

    def answer(self, answer):  # check answer, if true stop the game
        if answer == self.draw:
            self.draw = False
            print('correct guess!')
            return True
        else:
            print('incorrect guess.')
            return False

    def timer(self):  # if time runs out- stop the game
        print('time ran out')
        self.on_going = False
