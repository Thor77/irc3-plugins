# -*- coding: utf-8 -*-
from random import randint

import irc3
import requests
from irc3.plugins.command import command
from irc3.rfc import JOIN_PART_QUIT, PRIVMSG

from pyai import PyAI


@irc3.plugin
class AIPlugin(object):

    def __init__(self, bot):
        self.bot = bot
        self.ai = PyAI(db_prefix='lolbot')
        self.replyrate = 20
        if 'ai' in self.bot.config and \
                'replyrate' in self.bot.config['ai']:
                    self.replyrate = self.bot.config['ai']['replyrate']

    def create_gist(self, word):
        word_key = self.ai._words_key(word)
        if not self.ai.db.exists(word_key):
            return False
        relations = self.ai.db.hgetall(word_key)
        relations_formatted = ['- {}'.format(relation.decode(errors='replace'))
                               for relation in relations]
        relations_formatted.insert(0, word)
        relations_formatted.insert(1, '====')
        r = requests.post('https://api.github.com/gists', json={
            'description': 'Relations to {}'.format(word),
            'public': False,
            'files': {
                'relations.md': {
                    'content': '\n'.join(relations_formatted)
                }
            }
        })
        if not r:
            return '<Fehler>'
        return r.json()['html_url']

    @command
    def reply(self, mask, target, args):
        '''Reply

            %%reply <data>...
        '''
        data = ' '.join(args['<data>'])
        r = self.ai.process(data)
        if r:
            return r

    @command
    def connections(self, mask, target, args):
        '''Connections

            %%connections [<word>]
        '''
        word = args['<word>']
        if word:
            word = word.lower()
            word_key = self.ai._words_key(word)
            if self.ai.db.exists(word_key):
                gist_url = self.create_gist(word)
                return '"{}" hat {} Verbindungen! ' \
                    'Du kannst sie dir hier ansehen: {}'.format(
                        word, self.ai.db.hlen(word_key), gist_url
                    )
            else:
                return 'Ich kenne dieses Wort nicht :('
        else:
            return 'Ich kenne {} Wörter!'.format(
                len(self.ai.db.keys(self.ai._words_key('*')))
            )

    @irc3.event(PRIVMSG)
    def ai_process_reply(self, mask=None, event=None, target=None, data=None):
        cmd_sep = self.bot.config['irc3.plugins.command']['cmd']
        if event != 'PRIVMSG' or not target.startswith('#') or \
                data.startswith(cmd_sep):
                    return
        replyrate = self.replyrate
        if self.bot.nick in data:
            replyrate *= 2
        replyrate = 100 if replyrate > 100 else replyrate
        self.ai.learn(data)
        if randint(0, 100) < replyrate and not self.bot.muted:
            r = self.ai.reply(data)
            if r:
                self.bot.privmsg(target, r)

    @irc3.event(JOIN_PART_QUIT)
    def join_part_quit(self, mask=None, event=None, channel=None, data=None):
        if self.bot.muted:
            return
        nick = mask.split('!')[0].lower()
        r = self.ai.reply(nick)
        if r:
            self.bot.privmsg(channel, r)
