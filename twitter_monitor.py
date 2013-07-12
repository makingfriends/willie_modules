import twitter
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

    def monitor(willie):
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
            time.sleep(10)
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
                        '@%s was mentioned on twitter: %s' % (
                            willie.config.twitter.monitor_user, status.text))
            except twitter.TwitterError, e:
                willie.msg('Could not poll twitter: %s' % e)
            except Exception, e:
                willie.msg('General twitter polling error: %s' % e)


    t = threading.Thread(target=monitor, args=(willie,))
    t.start()

