import re
import time
import requests
import threading


def setup(willie):
    if not willie.config.has_section('github'):
        willie.config.add_section('github')

    if not willie.config.has_option('github', 'channel'):
        willie.config.parser.set('github', 'channel', '')

    if not willie.config.has_option('github', 'username'):
        willie.config.parser.set('github', 'username', '')
    
    if not willie.config.has_option('github', 'orgname'):
        willie.config.parser.set('github', 'orgname', '')

    if not willie.config.has_option('github', 'token'):
        willie.config.parser.set('github', 'token', '')

    t = threading.Thread(target=github_org_monitor, args=(willie,))
    t.start()


def github_org_monitor(willie):
    renderer = EventRenderer()
    
    def sayer(evt):
        for line in renderer.render(evt):
            willie.msg(willie.config.github.channel, line)

    feed = '/users/%s/events/orgs/%s' % (
        willie.config.github.username,
        willie.config.github.orgname
    )

    poller = GHEventPoller(willie.config.github.token, feed, sayer)
    
    while True:
        poller.start()


def get(endpoint, tok, etag=None):
    headers= {
        'Authorization': 'token %s' % tok
    }
    if etag:
        headers['If-None-Match'] = etag

    response = requests.get('https://api.github.com' + endpoint, headers=headers)
    if response.status_code >= 200 and response.status_code < 400:
        if etag and response.status_code == 304:
            return etag, response.headers['x-poll-interval'], [] # nothing new
        # we won't worry about pagination here because this is mostly used for polling
        return response.headers['etag'], response.headers['x-poll-interval'], response.json()
    raise Exception('Error contacting github: ' + str(response.status_code))


class EventRenderer(object):
    def render_PushEvent(self, event):
        ret = []
        reponame = event['repo']['name']

        ret.append('%s: %s pushed %d commits...' % (
            reponame, event['actor']['login'], len(event['payload']['commits'])))

        for commit in event['payload']['commits']:
            ret.append('%s: %s' % (
                reponame, commit['message'][:(80 - (len(reponame) + 2))]))
            ret.append('%s: review: https://github.com/%s/commit/%s' % (
                reponame, reponame, commit['sha'][:8]))

        return ret

    def render(self, event):
        renderer = getattr(self, 'render_%s' % event['type'], None)
        if renderer:
            return renderer(event)
        else:
            return ['%s did unknown event %s' % (event['actor']['login'], event['type'])]


class GHEventPoller(object):
    def __init__(self, token, feed, on_event=lambda x: x):
        self.poll_interval = 1 # second
        self.etag = None
        self.token = token
        self.feed = feed
        self.on_event = on_event

    def start(self):
        self.etag, interval, resp = get(self.feed, self.token)
        last_id = resp[0]['id']
        while True:
            # sleep(interval) # be well-behaved
            time.sleep(2)
            self.etag, interval, resp = get(self.feed, self.token, etag=self.etag)
            if len(resp):
                for obj in resp:
                    if last_id == obj['id']:
                        break # we got back to where we last were
                    self.on_event(obj)
                last_id = resp[0]['id']
