import time

import requests

from pyai import PyAI

pod = ''
profile_id = ''

profile_url = pod + '/people/' + profile_id + '/stream.json'
ai = PyAI(db_prefix='lolbot')


# fetch posts from diaspora
max_time = int(time.mktime(time.gmtime()))
days_left = 100
posts_text = []
while days_left > 0 and max_time > 0:
    r = requests.get(profile_url, params={'max_time': max_time})
    if r.status_code != requests.codes.ok:
        continue
    for post in r.json():
        if 'text' not in post or post['post_type'] != 'StatusMessage':
            continue
        post_text = post['text']
        if post_text not in posts_text:
            posts_text.append(post_text)
    max_time = max_time - 84600  # <- 1 day
    days_left -= 1

print('learning from', len(posts_text), 'posts...')
for post_text in posts_text:
    ai.learn(post_text)
print('done')
