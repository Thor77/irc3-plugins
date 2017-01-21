import irc3
from irc3.plugins.command import command

from ai_plugin import AIPlugin, FILTER_EAT


@irc3.plugin
class IgnorePlugin(object):
    def __init__(self, bot):
        self.ignored = []

        # add filter to ai_plugin
        aiplugin_instance = bot.get_plugin(AIPlugin)
        aiplugin_instance.filters.append(
            (FILTER_EAT, lambda mask, nick, message: nick in self.ignored)
        )

    @command(permission='admin')
    def ignore(self, mask, target, args):
        '''Ignore <nick> for ai-replies (privmsg + join/part)

            %%ignore <nick>
        '''
        nick = args['<nick>']
        if nick in self.ignored:
            return '"{}" wird schon ignoriert!'.format(nick)
        else:
            self.ignored.append(nick)
            return 'Ich ignoriere "{}" jetzt!'.format(nick)

    @command(permission='admin')
    def allow(self, mask, target, args):
        '''Allow <nick> again for ai-replies (privmsg + join/part)

            %%allow <nick>
        '''
        nick = args['<nick>']
        if nick not in self.ignored:
            return 'Dieser Nutzer wird noch nicht ignoriert!'
        else:
            self.ignored.remove(nick)
            return '"{}" wird jetzt nicht mehr ignoriert!'.format(nick)

    @command
    def ignored(self, mask, target, args):
        '''List ignored nicks

            %%ignored
        '''
        if not self.ignored:
            return 'Es werden noch keine Nutzer ignoriert!'
        return 'Ich ignoriere momentan diese Nutzer: {}'.format(
            ', '.join(self.ignored)
        )
