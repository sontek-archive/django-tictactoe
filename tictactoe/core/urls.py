from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from tictactoe.core.views import game_list, create_computer_game, view_game, create_move

urlpatterns = patterns('core.views',
    url(r'^$', game_list, name='game_list'),
    url(r'^games/$', game_list, name='game_list'),
    url(r'^games/create_computer/$', create_computer_game, name='create_computer_game'),
    url(r'^games/(?P<game_id>\d+)/$', view_game, name='view_game'),
    url(r'^games/(?P<game_id>\d+)/create_move$', create_move, name='create_move'),
)
