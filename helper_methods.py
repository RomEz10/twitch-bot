
def parse_command(msg):
    # separate command from additional arguments
    if msg.find(' ') != -1:  # check if there are args
        command = msg[1:msg.find(' ')]  # splice the ! and the arg after the command
        arguments_string = msg[msg.find(' ') + 1:]  # get arg - arg is the word after the command
        arguments_array = []
        for i in range(0, str(arguments_string).count(' ')):
            arguments_array.append(arguments_string[:arguments_string.find(' ')])
            arguments_string = arguments_string[arguments_string.find(' ') + 1:]
        arguments_array.append(arguments_string)
    else:
        command = msg[1:]  # splice the ! there are not args
        arguments_array = []  # no args
    print('arg: ' + str(arguments_array) + ' command: ' + command)
    return command, arguments_array
