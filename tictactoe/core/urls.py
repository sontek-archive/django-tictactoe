from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from core.views import game_list, create_computer_game, view_game, create_move
from core.views import accept_invite

urlpatterns = patterns('core.views',
    url(r'^$', game_list, name='game_list'),
    url(r'^games/$', game_list, name='game_list'),
    url(r'^games/create_computer/$', create_computer_game, name='create_computer_game'),
    url(r'^games/(?P<game_id>\d+)/$', view_game, name='view_game'),
    url(r'^games/(?P<game_id>\d+)/create_move$', create_move, name='create_move'),
    url(r'^games/invite/(?P<key>.+)/$', accept_invite, name='accept_invite'),
    url(r'^socket\.io', 'socketio'),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

