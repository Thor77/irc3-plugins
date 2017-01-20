# -*- coding: utf-8 -*-
import irc3
from irc3.plugins.command import command
from time import time


@irc3.plugin
class MutePlugin(object):

    def __init__(self, bot):
        self.muted = False
        self.maxmute = int(bot.config.get('mute', {}).get('maxmute', 360))

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
        if not self.muted:
            self.muted = True
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
        if self.muted:
            self.muted = False
            return 'Ich rede jetzt wieder \o/'
        else:
            return 'Ich bin gar nicht stumm!'

    @command
    def muted(self, mask, target, args):
        '''Check if bot is muted

            %%muted
        '''
        if self.muted:
            return 'Ich bin momentan still (noch für {} Minuten)!'.format(
                int((self.mute_end - time()) / 60)
            )
        else:
            return 'LALALALALALALALA (nein)'

    @irc3.event(irc3.rfc.PRIVMSG)
    def check_mute(self, mask, event, target, data):
        if self.muted and time() >= self.mute_end:
            self.muted = False
