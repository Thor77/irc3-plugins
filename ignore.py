import irc3
from irc3.plugins.command import command

from ai_plugin import AIPlugin, FILTER_EAT


@irc3.plugin
class IgnorePlugin(object):
    def __init__(self, bot):
        self.bot = bot

        if self not in self.bot.db or '' not in self.bot.db[self]:
            # This workaround is required until
            # https://github.com/gawel/irc3/issues/127 is solved
            self.bot.db[self] = {'': []}

        # add filter to ai_plugin
        aiplugin_instance = bot.get_plugin(AIPlugin)
        aiplugin_instance.filters.append(
            (
                FILTER_EAT,
                lambda mask, nick, message:
                    nick.lower() in self.bot.db[self]['']
            )
        )

    @command(permission='admin')
    def ignore(self, mask, target, args):
        '''Ignore <nick> for ai-replies (privmsg + join/part)

            %%ignore <nick>
        '''
        nick = args['<nick>']
        nick_l = nick.lower()
        if nick_l in self.bot.db[self]['']:
            return '"{}" wird schon ignoriert!'.format(nick)
        else:
            self.bot.db[self][''].append(nick_l)
            return 'Ich ignoriere "{}" jetzt!'.format(nick)

    @command(permission='admin')
    def allow(self, mask, target, args):
        '''Allow <nick> again for ai-replies (privmsg + join/part)

            %%allow <nick>
        '''
        nick = args['<nick>']
        nick_l = nick.lower()
        if nick_l not in self.bot.db[self]['']:
            return 'Dieser Nutzer wird noch nicht ignoriert!'
        else:
            self.bot.db[self][''].remove(nick_l)
            return '"{}" wird jetzt nicht mehr ignoriert!'.format(nick)

    @command
    def ignored(self, mask, target, args):
        '''List ignored nicks

            %%ignored
        '''
        if not self.bot.db[self]['']:
            return 'Es werden noch keine Nutzer ignoriert!'
        return 'Ich ignoriere momentan diese Nutzer: {}'.format(
            ', '.join(self.bot.db[self][''])
        )
