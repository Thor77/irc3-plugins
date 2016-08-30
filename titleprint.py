# -*- coding: utf-8 -*-
import logging
import re

import irc3
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger('irc3')


def clean_title(title):
    title = title.replace('\\', '')
    return title.strip()


def fetch_title(url):
    '''
    Fetch title of an website

    :param url: url of the website
    :type url: str
    '''
    logger.debug('Fetching title for "%s"', url)
    try:
        response = requests.get(url, timeout=5)
    except Exception as e:
        logger.warning('Couldn\'t fetch %s', url)
        logger.debug(e)
        return None
    if response.headers.get('content-type', '').startswith('text/'):
        try:
            bs = BeautifulSoup(response.text, 'html.parser')
            return clean_title(bs.title.string)
        except Exception as e:
            logger.warning('Couldn\'t fetch title from %s', url)
            logger.debug(e)


@irc3.plugin
class URLPrintPlugin(object):
    def __init__(self, bot):
        self.bot = bot
        self.bot.blocked_domains = ['twitter.com']
        self.re_url = re.compile(
            r'https?://(.+\.)?(?P<domain>[\w-]+\.\w+)(/[^^\s]*)?'
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
