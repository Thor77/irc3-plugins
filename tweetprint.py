# -*- coding: utf-8 -*-
import html
import re

import irc3
from twitter.api import TwitterHTTPError


@irc3.plugin
class TweetPrintPlugin(object):
    def __init__(self, bot):
        self.bot = bot
        self.re_tweet = re.compile(
            r'https?:\/\/(w{3}\.)?twitter.com\/[\w\d_]+\/status\/(\d{15,20})'
        )

    @irc3.event(irc3.rfc.PRIVMSG)
    def tweet(self, mask, event, target, data):
        tweets = []
        for _, status_id in self.re_tweet.findall(data):
            try:
                tweet = self.bot.get_social_connection().statuses.show(
                    id=status_id
                )
            except TwitterHTTPError:
                continue
            tweet_text = html.unescape(tweet['text'])
            # first expand image-urls
            entities = tweet.get('extended_entities', tweet['entities'])
            for media in entities.get('media', []):
                current_url = media['url']
                media_type = media['type']
                if media_type == 'video':
                    # take expanded-url for videos
                    long_url = media.get('expanded_url', current_url)
                else:
                    # take media_url_https or media_url for everything else
                    long_url = media.get(
                        'media_url_https', media.get('media_url', current_url)
                    )
                tweet_text = tweet_text.replace(current_url, long_url)
            # now expand normal urls
            for url in tweet['entities'].get('urls', []):
                tweet_text = tweet_text.replace(url['url'], url.get(
                    'expanded_url', url['url'])
                )
            tweets.append('@{handle}: {tweet}'.format(
                handle=tweet['user']['screen_name'], tweet=tweet_text))
        if tweets:
            self.bot.privmsg(target, ' | '.join(tweets))
