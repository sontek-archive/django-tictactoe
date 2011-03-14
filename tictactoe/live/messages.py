from redis import Redis
from django.conf import settings

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')

class MessageChannel(object):
    def __init__(self):
        self.red = Redis(REDIS_HOST)

    def publish(self, chan, msg):
        """ Handle incoming message for everyone. """
        self.red.publish(chan, msg)

    def subscribe(self, chan):
        self.red.subscribe(chan)

    def updates(self):
        event_list = []
        for msg in self.red.listen():
            if msg['data'] == 'unsubscribe':
                self.red.unsubscribe(msg['channel'])
            event_list.append(msg['data'])
        return event_list
