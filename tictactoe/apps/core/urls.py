from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from core.views import (game_list,
    create_computer_game, 
    view_game, 
    create_move,
    accept_invite,
    socketio,
)

urlpatterns = patterns('core.views',
    url(
        regex=r'^$', 
        view=game_list, 
        name='game_list'
    ),
    url(
        regex=r'^games/$',
        view=game_list,
        name='game_list'
    ),
    url(
        regex=r'^games/create_computer/$', 
        view=create_computer_game, 
        name='create_computer_game'
    ),
    url(
        regex=r'^games/(?P<game_id>\d+)/$',
        view=view_game,
        name='view_game'
    ),
    url(
        regex=r'^games/(?P<game_id>\d+)/create_move$', 
        view=create_move,
        name='create_move'
    ),
    url(
        regex=r'^games/invite/(?P<key>.+)/$',
        view=accept_invite,
        name='accept_invite'
    ),
    url(
        regex=r'^socket\.io',
        view=socketio
    ),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
