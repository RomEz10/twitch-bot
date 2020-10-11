import socket
import asyncio
import twitch_api

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

    async def send_bulk(self, chan, msgs):
        for msg in msgs:
            full_msg = "PRIVMSG" + " #" + chan + " :" + msg + LINE_ENDINGS
            self.writer.write(full_msg.encode(encoding))
        await self.writer.drain()

    async def send_whisper(self, chan, target, msg):
        full_msg = "PRIVMSG" + " #" + chan + " :/w " + target + ' ' + msg + LINE_ENDINGS
        print(full_msg)
        self.writer.write(full_msg.encode(encoding))
        await self.writer.drain()

    async def send_whisper_bulk(self, chan, msgs, targets=None):
        # Requires either msgs list with each item being a dict with 'text' and 'target' keys,
        # or a msgs list and targets list.
        # Sends a number of whispers
        # If targets is provided both msgs and targets are lists, if not, msgs is a list of dict with text and target
        # Targets are always treated as twitch_ids for now.
        if targets:
            targets = twitch_api.get_username_from_id_bulk({'id': targets})
            for msg, target in zip(msgs, targets):
                full_msg = "PRIVMSG" + " #" + chan + " :/w " + target + ' ' + msg + LINE_ENDINGS
                self.writer.write(full_msg.encode(encoding))
        else:
            for msg in msgs:
                target = twitch_api.get_username_from_id(msg['target'])
                full_msg = "PRIVMSG" + " #" + chan + " :/w " + target + ' ' + msg['text'] + LINE_ENDINGS
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
        self.writer.write(("PASS " + auth + LINE_ENDINGS + "NICK " + botnick + LINE_ENDINGS).encode(encoding))
        self.writer.write(("JOIN #" + channel + LINE_ENDINGS).encode(encoding))
        await self.writer.drain()
        asyncio.create_task(twitch_api.bot_joined_channel(channel))

    async def get_msg(self):
        text = await self.reader.readline()  # receive the text, if empty socket was closed
        if text:
            if str(text)[2:16] == ':tmi.twitch.tv':  # first 2 chars are trash+checking if its session open confirmation
                return await self.get_msg()  # do not pass the first message, its not a user msg, return the next one
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
            server = self.server
            channel = self.channel
            botnick = self.botnick
            auth = self.auth
            self.__init__()
            await self.connect(server, channel, botnick, auth)
            return await self.get_msg()
