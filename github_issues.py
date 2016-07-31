# -*- coding: utf-8 -*-
import re

import irc3
import requests


@irc3.plugin
class GithubIssuesPlugin(object):

    def __init__(self, bot):
        self.bot = bot
        self.re_issues = re.compile(
            r'(?:^|\s+)(?P<user_org>[\d\w\-._]+/)?'
            r'(?P<repo>[\d\w\-._]+)?#(?P<id>\d+)'
        )
        gh_conf = self.bot.config.get('github_issues', {})
        self.default_user_org = gh_conf.get('user_org', '')
        self.default_repo = gh_conf.get('repo')

    @irc3.event(irc3.rfc.PRIVMSG)
    def issue(self, mask, event, target, data):
        issues = []
        for match in self.re_issues.finditer(data):
            match = match.groupdict()
            if match['user_org']:
                user_org = match['user_org'][:-1]
            else:
                if not self.default_user_org:
                    return
                user_org = self.default_user_org
            if match['repo']:
                repo = match['repo']
            else:
                if not self.default_repo:
                    return
                repo = self.default_repo
            url = 'https://api.github.com/repos/{}/{}/issues/{}'.format(
                user_org, repo, match['id']
            )
            r = requests.get(url)
            if r:
                r = r.json()
                issues.append('{} ({})'.format(r['html_url'], r['title']))
        if issues:
            self.bot.privmsg(target, ' | '.join(issues))
