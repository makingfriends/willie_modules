import twitter
import tweepy, tweepy.streaming
import json
import time
import threading


CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''


def setup(willie):
    if not willie.config.has_section('twitter'):
        willie.config.add_section('twitter')

    if not willie.config.has_option('twitter', 'channel'):
        willie.config.parser.set('twitter', 'channel', '')

    if not willie.config.has_option('twitter', 'monitor_user'):
        willie.config.parser.set('twitter', 'monitor_user', '')
    
    if not willie.config.has_option('twitter', 'consumer_key'):
        willie.config.parser.set('twitter', 'consumer_key', CONSUMER_KEY)

    if not willie.config.has_option('twitter', 'consumer_secret'):
        willie.config.parser.set('twitter', 'consumer_secret', CONSUMER_SECRET)

    if not willie.config.has_option('twitter', 'access_token'):
        willie.config.parser.set('twitter', 'access_token', ACCESS_TOKEN)

    if not willie.config.has_option('twitter', 'access_token_secret'):
        willie.config.parser.set('twitter', 'access_token_secret', ACCESS_TOKEN_SECRET)

    t = threading.Thread(target=monitor_streaming, args=(willie,))
    t.start()


def monitor_streaming(willie):
    def say_tweet(tweet):
        link = 'https://twitter.com/%s/status/%s' % (tweet['user']['screen_name'], tweet['id'])
        if is_monitor_user(tweet['user']['screen_name']):
            willie.msg(willie.config.twitter.channel, 
                '@%s says on Twitter: "%s" [ %s ]' % (
                tweet['user']['screen_name'], tweet['text'], link))
        elif willie.config.twitter.monitor_user in tweet['text']:
            willie.msg(willie.config.twitter.channel,
                '@%s was mentioned on Twitter by @%s: "%s" [ %s ]' % (
                willie.config.twitter.monitor_user,
                tweet['user']['screen_name'], tweet['text'], link))

    def is_monitor_user(name):
        return name.lower() == willie.config.twitter.monitor_user.lower()

    class Listener(tweepy.streaming.StreamListener):
        def on_data(self, data):
            activity = json.loads(data)
            if 'text' in activity and 'user' in activity \
                    and 'screen_name' in activity['user']:
                if is_monitor_user(activity['user']['name']) \
                        or willie.config.twitter.monitor_user in activity['text']:
                    say_tweet(activity)
            elif 'event' in activity and activity['event'] == 'follow':
                if is_monitor_user(activity['target']['screen_name']):
                    willie.msg(willie.config.twitter.channel,
                        '@%s was followed by @%s on Twitter! [ %s ]' % (
                            willie.config.twitter.monitor_user,
                            activity['source']['screen_name'],
                            'https://twitter.com/%s' % activity['source']['screen_name']))
            return True

        def on_reror(self, status):
            willie.msg(willie.config.twitter.channel, 'Error connecting to twitter: ' + str(status))
            return True

    auth = tweepy.OAuthHandler(willie.config.twitter.consumer_key,
                               willie.config.twitter.consumer_secret)
    auth.set_access_token(willie.config.twitter.access_token,
                          willie.config.twitter.access_token_secret)

    listener = Listener()
    stream = tweepy.Stream(auth, listener)
    stream.userstream()


def monitor_polling(willie):
    if not willie.config.twitter.monitor_user or not willie.config.twitter.channel:
        print 'invalid twitter config: no monitor_user or channel set'
        return
    
    api = twitter.Api(
        consumer_key=willie.config.twitter.consumer_key,
        consumer_secret=willie.config.twitter.consumer_secret,
        access_token_key=willie.config.twitter.access_token,
        access_token_secret=willie.config.twitter.access_token_secret
    )
    # verify credentials, exit if invalid
    try:
        api.VerifyCredentials()
    except twitter.TwitterError:
        willie.msg(willie.config.twitter.channel, 'Failed to connect to twitter. Invalid credentials.')
        return

    recents = api.GetUserTimeline(screen_name=willie.config.twitter.monitor_user)
    mentions = api.GetMentions()

    while True:
        time.sleep(60)
        try:
            new_recents = api.GetUserTimeline(
                screen_name=willie.config.twitter.monitor_user,
                since_id=recents[0].id
            )
            if len(new_recents):
                recents = new_recents
            for status in new_recents:
                willie.msg(
                    willie.config.twitter.channel,
                    '@%s says on twitter: %s' % (willie.config.twitter.monitor_user, status.text)
                )

            new_mentions = api.GetMentions(since_id=mentions[0].id)
            if len(new_mentions):
                mentions = new_mentions
            for status in new_mentions:
                willie.msg(
                    willie.config.twitter.channel,
                    '@%s was mentioned by %s on twitter: %s' % (
                        willie.config.twitter.monitor_user, 
                        status.user,
                        status.text))
        except twitter.TwitterError, e:
            willie.msg(willie.config.twitter.channel, 'Could not poll twitter: %s' % e)
        except Exception, e:
            willie.msg(willie.config.twitter.channel, 'General twitter polling error: %s' % e)
