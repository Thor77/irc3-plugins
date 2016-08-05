# -*- coding: utf-8 -*-
import re

import irc3
from twitter.api import TwitterHTTPError


@irc3.plugin
class TweetPrintPlugin(object):
    def __init__(self, bot):
        self.bot = bot
        self.re_tweet = re.compile(
            'https?:\/\/(w{3}\.)?twitter.com\/[\w\d_]+\/status\/(\d{15,20})'
        )

    @irc3.event(irc3.rfc.PRIVMSG)
    def tweet(self, mask, event, target, data):
        tweets = []
        for _, status_id in self.re_tweet.findall(data):
            try:
                tweet = self.bot.get_social_connection().statuses.show(
                    id=status_id, trim_user=True
                )
            except TwitterHTTPError:
                continue
            tweet_text = tweet['text']
            # first expand image-urls
            for media in tweet['entities'].get('media', []):
                tweet_text = tweet_text.replace(media['url'], media.get(
                    'media_url_https', media.get(
                        'media_url', media['url'])
                    )
                )
            # now expand normal urls
            for url in tweet['entities'].get('urls', []):
                tweet_text = tweet_text.replace(url['url'], url.get(
                    'expanded_url', url['url'])
                )
            tweets.append(tweet_text)
        if tweets:
            self.bot.privmsg(target, ' | '.join(tweets))
