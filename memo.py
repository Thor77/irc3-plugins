# -*- coding: utf-8 -*-
from collections import namedtuple

import irc3
from irc3.plugins.command import command

Memo = namedtuple('Memo', ['text', 'sender'])


@irc3.plugin
class MemoPlugin(object):
    def __init__(self, bot):
        self.bot = bot
        self.memo_store = {}

    @command
    def memo(self, mask, target, args):
        '''Create a memo for a nick

            %%memo <nick> <message>...
        '''
        sender = mask.split('!')[0]
        receiver = args['<nick>']
        receiver_lower = receiver.lower()
        message = ' '.join(args['<message>'])
        memo = Memo(message, sender)
        if receiver_lower in self.memo_store:
            self.memo_store[receiver_lower].append(memo)
        else:
            self.memo_store[receiver_lower] = [memo]
        return 'Successfully added memo for {}!'.format(receiver)

    @irc3.event(irc3.rfc.JOIN)
    def join(self, mask=None, event=None, channel=None):
        nick = mask.split('!')[0]
        nick_lower = nick.lower()
        if nick_lower in self.memo_store:
            for memo in self.memo_store.get(nick_lower, []):
                memo_formatted = '{}: {} (from {})'.format(
                    nick, memo.text, memo.sender)
                self.bot.privmsg(channel, memo_formatted)
            del self.memo_store[nick_lower]
