from django.conf.urls.defaults import (patterns, include, url, handler500,
        handler404)
from django.contrib import admin
admin.autodiscover()

from core.views import (
    create_move,
    view_game,
    socketio,
)
urlpatterns = patterns('',
    url(
        regex=r'^create_move/(?P<game_id>\d+)/$',
        view=create_move,
        name='create_move'
    ),
    url(
        regex=r'^view_game/(?P<game_id>\d+)/$',
        view=view_game,
        name='view_game'
    ),
    url(
        regex=r'^socket\.io',
        view=socketio,
        name='socketio'
    ),
    (r'^admin/', include(admin.site.urls)),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

