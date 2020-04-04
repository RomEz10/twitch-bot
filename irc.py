import socket
import asyncio

encoding = 'utf-8'
LINE_ENDINGS = '\r\n'    # This is appended to all messages sent by the socket (should always be CRLF)


class IRC:
    irc = socket.socket()

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ''
        self.channel = ''
        self.botnick = ''
        self.auth = ''
        self.writer = asyncio.StreamWriter
        self.reader = asyncio.StreamReader

    @staticmethod
    def irc_command(msg):
        command = msg[msg.find(' ')+1:msg.find(' ', msg.find(' ')+1)]
        return command

    async def send(self, chan, msg):
        full_msg = "PRIVMSG" + " #" + chan + " :" + msg + LINE_ENDINGS
        print(full_msg)
        self.writer.write(full_msg.encode(encoding))
        await self.writer.drain()

    async def send_whisper(self, chan, target, msg):
        full_msg = "PRIVMSG" + " #" + chan + " :/w " + target + ' ' + msg + LINE_ENDINGS
        print(full_msg)
        #self.irc.send(full_msg.encode(encoding))
        self.writer.write(full_msg.encode(encoding))
        await self.writer.drain()

    async def connect(self, server, channel, botnick, auth):
        # defines the socket
        self.server = server
        self.channel = channel
        self.botnick = botnick
        self.auth = auth
        print("connecting to:" + server)
        self.reader, self.writer = await asyncio.open_connection(server, 6667)
        #self.irc.connect((server, 6667))  # connects to the server
        #self.irc.send(("PASS " + auth + LINE_ENDINGS + "NICK " + botnick + LINE_ENDINGS).encode(encoding))
        self.writer.write(("PASS " + auth + LINE_ENDINGS + "NICK " + botnick + LINE_ENDINGS).encode(encoding))
        #self.irc.send(("JOIN #" + channel + LINE_ENDINGS).encode(encoding))  # join the chan
        self.writer.write(("JOIN #" + channel + LINE_ENDINGS).encode(encoding))
        await self.writer.drain()

    async def get_msg(self):
        text = await self.reader.readline()  # receive the text, if empty socket was closed
        if text:
            if str(text)[2:16] == ':tmi.twitch.tv':  # first 2 chars are trash- checking if its session open confirmation
                print('initiated')
                return await self.get_msg()  # do not pass the first message, its not a user message. return the next one
            if str(text).find('PING') != -1:
                self.writer.write('PONG :tmi.twitch.tv'.encode(encoding))
                await self.writer.drain()
                return await self.get_msg()
            text = text.decode(encoding)
            print('raw: ' + text)
            msg = text[text.rfind(':')+1:-2]  # parse the IRC string to get the msg -2 removes the \r\n in the end
            if self.irc_command(text) == 'PRIVMSG':
                username = text[text.find(':') + 1:text.find('!')]
                return msg, username
            else:
                return await self.get_msg()
        else:
            print('closed')
            #self.irc.close()
            #self.irc = socket.socket()
            server = self.server
            channel = self.channel
            botnick = self.botnick
            auth = self.auth
            self.__init__()
            await self.connect(server, channel, botnick, auth)
            return self.get_msg()
