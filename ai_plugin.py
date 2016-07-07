# -*- coding: utf-8 -*-
from random import randint

import irc3
import requests
from irc3.plugins.command import command
from irc3.rfc import JOIN_PART_QUIT, PRIVMSG
from markov import MarkovPy
from markov.stores import Pickle


@irc3.plugin
class AIPlugin(object):

    def __init__(self, bot):
        self.bot = bot
        self.ai = MarkovPy(store=Pickle('lolbot.pickle'))
        self.replyrate = self.bot.config.get('ai', {}).get('replyrate', 20)

    def create_gist(self, word):
        if not self.ai.store.known(word):
            return False
        relations = self.ai.store.next_words(word)
        relations_formatted = ['- {} *{}*'.format(word, score)
                               for word, score in relations]
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
            if self.ai.store.known(word):
                gist_url = self.create_gist(word)
                return '"{}" hat {} Verbindungen! ' \
                    'Du kannst sie dir hier ansehen: {}'.format(
                        word, self.ai.store.relation_count(word), gist_url
                    )
            else:
                return 'Ich kenne dieses Wort nicht!'
        else:
            return 'Ich kenne {} Wörter!'.format(len(self.ai))

    @irc3.event(PRIVMSG)
    def ai_process_reply(self, mask=None, event=None, target=None, data=None):
        cmd_sep = self.bot.config['irc3.plugins.command']['cmd']
        if event != 'PRIVMSG' or not target.startswith('#') or \
                data.startswith(cmd_sep):
                    return
        replyrate = self.replyrate
        if self.bot.nick in data:
            replyrate /= 2
        replyrate = 1 if replyrate < 1 else replyrate
        self.ai.learn(data)
        if randint(0, replyrate) == 0 and not self.bot.muted:
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
