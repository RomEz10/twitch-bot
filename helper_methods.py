import twitch_api


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


def all_msg_emotes(channel, msg):
    # returns a list with all the emotes used in the message
    emotes = twitch_api.get_all_emotes(channel)
    emotes_in_msg = []
    for i in range(0, len(msg)):
        space = msg.find(' ')
        if space != -1:
            word = msg[:space]
            msg = msg[space+1:]
        else:
            word = msg
        if word in emotes:
            emotes_in_msg.append(word)
    return emotes_in_msg
