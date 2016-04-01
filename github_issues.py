# -*- coding: utf-8 -*-
import re

import irc3
import requests
from irc3.plugins.command import command


@irc3.plugin
class GithubIssuesPlugin(object):

    def __init__(self, bot):
        self.bot = bot
        self.re_issues = re.compile(r'(?:^|\s+|\()#(\d*)\b')
        self.repo_link = None
        if 'github_issues' in self.bot.config and \
                'user_org' in self.bot.config['github_issues'] and \
                'repo' in self.bot.config['github_issues']:
                    self.repo_link = bot.config['github_issues']['user_org'] +\
                                    '/' + bot.config['github_issues']['repo']

    @irc3.event(irc3.rfc.PRIVMSG)
    def issue(self, mask, event, target, data):
        if not self.repo_link or not target.startswith('#'):
            return
        issues = []
        for issue in self.re_issues.findall(data):
            url = 'https://api.github.com/repos/{}/issues/{}'.format(
                self.repo_link, issue
            )
            r = requests.get(url)
            if r:
                r = r.json()
                issues.append('{} ({})'.format(r['html_url'], r['title']))
        if issues:
            self.bot.privmsg(target, ' | '.join(issues))
