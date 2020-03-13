import socket

encoding = 'utf-8'
LINE_ENDINGS = '\r\n'    # This is appended to all messages sent by the socket (should always be CRLF)


class IRC:
    irc = socket.socket()

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, chan, msg):
        full_msg = "PRIVMSG" + " #" + chan + " :" + msg + LINE_ENDINGS
        print(full_msg)
        self.irc.send(full_msg.encode(encoding))

    def send_whisper(self, chan, target, msg):
        full_msg = "PRIVMSG" + " #" + chan + " :/w " + target + ' ' + msg + LINE_ENDINGS
        print(full_msg)
        self.irc.send(full_msg.encode(encoding))

    def connect(self, server, channel, botnick, auth):
        # defines the socket
        print("connecting to:" + server)
        self.irc.connect((server, 6667))  # connects to the server
        self.irc.send(("PASS " + auth + LINE_ENDINGS + "NICK " + botnick + LINE_ENDINGS ).encode(encoding))
        self.irc.send(("JOIN #" + channel + LINE_ENDINGS).encode(encoding))  # join the chan

    def get_msg(self):
        text = self.irc.recv(4096)  # receive the text
        if str(text)[2:16] == ':tmi.twitch.tv':  # first two chars are trash- checking if its session open confirmation
            print('initiated')
            return self.get_msg()  # do not pass the first message, its not a user message. return the next one
        if str(text).find('PING') != -1:
            self.irc.send(('PONG ' + str(text).split()[1] + 'rn').encode(encoding))
            return self.get_msg()
        text = text.decode(encoding)
        print('raw: ' + text)
        msg = text[text.rfind(':') + 1:-2]  # parse the IRC string to get the msg -2 removes the \r\n in the end of msg
        username = text[text.find(':') + 1:text.find('!')]
        return msg, username
