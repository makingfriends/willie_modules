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


def post(config, url, data):
    base_url = config.logger.base_url.rstrip('/')
    return _wrap_response(requests.post(base_url + url, 
        data=json.dumps(data), 
        headers={
            'Authorization': "Token %s" % config.logger.api_key,
            'Content-Type': 'application/json'
        },
        allow_redirects=True
    ))


def setup(willie):
    if not willie.config.has_section('logger'):
        willie.config.add_section('logger')
    
    if not willie.config.has_option('logger', 'channels'):
        willie.config.parser.set('logger', 'channels', willie.config.core.channels)

    if not willie.config.has_option('logger', 'base_url'):
        willie.config.parser.set('logger', 'base_url', BASE_URL)

    if not willie.config.has_option('logger', 'api_key'):
        willie.config.parser.set('logger', 'api_key', API_KEY)


def logger(willie, trigger):
    if trigger.sender in willie.config.logger.channels:
        success, resp = post(willie.config, '/irc/messages/', {
            'message': str(trigger),
            'channel': {'name': trigger.sender},
            'user': {'name': trigger.user}
        })
        if not success:
            willie.say('Derp, I am having trouble conncting to the log server. Please tell someone to fix this. Error was: %r' % resp)

logger.rule = ['(.*)']
logger.priority = 'low'
