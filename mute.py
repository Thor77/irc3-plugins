# -*- coding: utf-8 -*-
import irc3
from irc3.plugins.command import command
from time import time


@irc3.plugin
class MutePlugin(object):

    def __init__(self, bot):
        self.bot = bot
        self.bot.muted = False
        self.maxmute = 360
        if 'mute' in self.bot.config and \
                'maxmute' in self.bot.config['mute']:
                    try:
                        self.maxmute = int(self.bot.config['mute']['maxmute'])
                    except:
                        # cant set custom maxmute
                        # continue anyway
                        pass

    @command
    def mute(self, mask, target, args):
        '''Mute AI-Output for <duration> minutes

            %%mute [<duration>]
        '''
        duration = args['<duration>'] if args['<duration>'] else self.maxmute
        try:
            duration = int(duration)
        except ValueError:
            return 'Das ist keine valide Minuten-Anzahl!'
        duration = self.maxmute if duration > self.maxmute else duration
        if not self.bot.muted:
            self.bot.muted = True
            self.mute_start = time()
            self.mute_end = self.mute_start + (duration * 60)  # => min
            return 'Ich bin jetzt für {} Minuten still!'.format(duration)
        else:
            return 'Ich bin doch schon still :('

    @command
    def unmute(self, mask, target, args):
        '''Unmute

            %%unmute
        '''
        if self.bot.muted:
            self.bot.muted = False
            return 'Ich rede jetzt wieder \o/'
        else:
            return 'Ich bin gar nicht stumm!'

    @irc3.event(irc3.rfc.PRIVMSG)
    def muted(self, mask, event, target, data):
        if self.bot.muted and time() >= self.mute_end:
            self.bot.muted = False
