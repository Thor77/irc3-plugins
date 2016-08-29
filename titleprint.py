# -*- coding: utf-8 -*-
import re

import irc3
import requests
from bs4 import BeautifulSoup


def clean_title(title):
    title = title.replace('\\', '')
    return title.strip()


def fetch_title(url):
    '''
    Fetch title of an website

    :param url: url of the website
    :type url: str
    '''
    response = requests.get(url, timeout=5)
    if response.headers.get('content-type', '').startswith('text/'):
        try:
            bs = BeautifulSoup(response.text, 'html.parser')
            return clean_title(bs.title.string)
        except:
            return None


@irc3.plugin
class URLPrintPlugin(object):
    def __init__(self, bot):
        self.bot = bot
        self.bot.blocked_domains = ['twitter.com']
        self.re_url = re.compile(
            r'https?://(.+\.)?(?P<domain>\w+\.\w+)(/[^^\s]*)?'
        )

    @irc3.event(irc3.rfc.PRIVMSG)
    def url(self, mask, event, target, data):
        match = self.re_url.search(data)
        if match:
            if match.group('domain') in self.bot.blocked_domains:
                return
            title = fetch_title(match.group(0))
            if title:
                output_fmt = 'Title: {title}'
                self.bot.privmsg(target, output_fmt.format(title=title))
