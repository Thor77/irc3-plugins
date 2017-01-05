# -*- coding: utf-8 -*-
'''
Addon for AIPlugin
'''
import random

import irc3
from irc3.plugins.command import command
from irc3.plugins.cron import cron

DRINK_PHRASES = [
    'Prost!',
    'Vielen Dank {nick} :)',
    'Danke \o/',
    'YEAH \o/'
]

DRUNK_PHRASES = [
    'Es wird nicht mehr besser...',
    'WAAAAS NOCH MEHR?!',
    'Urgh',
    'Danke, nein.'
]


@irc3.plugin
class DrinkPlugin(object):
    def __init__(self, bot):
        self.config = bot.config.get('drink', {})
        self.max_level = self.config.get('max_level', 42)
        self.drunk_word = self.config.get('word', 'hiks')
        self.bot = bot

        self.drunk_level = 0

    @command
    def drink(self, mask, target, args):
        '''Drink some stuff

            %%drink
        '''
        if self.drunk_level >= self.max_level:
            return random.choice(DRUNK_PHRASES)
        self.drunk_level += 1
        return random.choice(DRINK_PHRASES).format(nick=mask.split('!')[0])

    @command(permission='admin')
    def drinkmax(self, mask, target, args):
        '''Set drunken to max

            %%drinkmax
        '''
        self.drunk_level = self.max_level
        return 'Jetzt bin ich betrunken...'

    @command
    def drunken(self, mask, target, args):
        '''Am I drunk?

            %%drunken
        '''
        if self.drunk_level == 0:
            return 'Ich bin nicht betrunken! Verhalte ich mich etwa so? oO'
        return 'Auf einer Skala von 0 bis {} bin ich {} betrunken!'.format(
            self.max_level, self.drunk_level
        )

    @cron('*/30 * * * *')
    def sober(plugin):
        if plugin.drunk_level <= 0:
            return
        plugin.drunk_level -= 1

    @irc3.extend
    def drunk_filter(plugin, message):
        if plugin.drunk_level == 0:
            return message
        words = message.split()
        unreplaced_words = words
        random.shuffle(unreplaced_words)
        replace_rate = random.randint(1, plugin.max_level) / plugin.max_level
        words_to_replace = int(len(words) * replace_rate)
        for word in unreplaced_words[:words_to_replace]:
            message = message.replace(word, plugin.drunk_word)
        return message
