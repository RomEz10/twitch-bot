import random
# when first starts should pick a word from a list of objects to draw and start a timer
# when either time ends or word is guesses correctly the game should end


class DrawGame:
    how_long = 0
    on_going = False
    choices = ['computer', 'camel', 'cup']
    draw = ''

    def timer(self):  # if time runs out- stop the game
        print('time ran out')
        self.on_going = False

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

