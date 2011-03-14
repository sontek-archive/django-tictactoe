import simplejson
from uuid import uuid4
from django.http import HttpResponse
from core.models import Game
from live.messages import MessageChannel

def updates(request):
    #games = Game.objects.get_by_user(request.user).values_list('id', flat=True)
    chan = MessageChannel()
    #for game_id in games:
    #    chan.subscribe('{0}#{1}'.format(str(uuid4()), game_id))
    chan.subscribe('#chan1')

    return json_response(chan.updates())

def publish(request):
    chan = MessageChannel()
    chan.publish('#chan1', 'hi2u')
    chan.publish('#chan1', 'hi2u')
    chan.publish('#chan1', 'hi2u')
    chan.publish('#chan1', 'hi2u5')
    chan.publish('#chan1', 'unsubscribe')
    return json_response({'success': True})

def json_response(value, **kwargs):
    kwargs.setdefault('content_type', 'text/plain; charset=UTF-8')
    return HttpResponse(simplejson.dumps(value), **kwargs)
