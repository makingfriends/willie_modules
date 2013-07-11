import json
import requests


API_KEY = '14e3d0ee0fa98acc57b2eb6fd0963f1fbf1987f7'
BASE_URL = 'http://localhost:8000/api'


def _wrap_response(resp):
    if resp.status_code >= 200 and resp.status_code <= 400:
        return True, json.loads(resp.content)
    if 'json' in resp.headers['content-type']:
        return False, json.loads(resp.content)
    return False, resp.status_code


def post(url, data):
    return _wrap_response(requests.post(url, 
        data=json.dumps(data), 
        headers={
            'Authorization': "Token %s" % API_KEY,
            'Content-Type': 'application/json'
        },
        allow_redirects=True
    ))


def setup(willie):
    if not willie.config.has_section('logger'):
        willie.config.add_section('logger')
    if not willie.config.has_option('logger', 'channels'):
        willie.config.parser.set('logger', 'channels', willie.config.core.channels)

    print 'logging channels:', willie.config.logger.channels

def logger(willie, trigger):
    print 'turd', trigger.sender, willie.config.logger.channels
    if trigger.sender in willie.config.logger.channels:
        success, resp = post(BASE_URL + '/irc/messages/', {
            'message': str(trigger),
            'channel': {'name': trigger.sender},
            'user': {'name': trigger.user}
        })
        if not success:
            willie.say('Derp, I am having trouble conncting to the log server. Please tell someone to fix this. Error was: %r' % resp)
            #willie.say('Error was: ' + str(resp))
    print 'logging: ', trigger.sender, trigger.hostmask, trigger.user, trigger.nick, ':', trigger
    print 'willie: ', type(willie), willie

def assoc(willie, trigger):
    print 'associating: ', 'balls'

logger.rule = ['(.*)']
logger.priority = 'low'