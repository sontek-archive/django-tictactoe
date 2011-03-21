from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TicTacToe.views.home', name='home'),
    url(r'', include('core.urls')),
    url(r'^users/', include('registration.urls')),
    url(r'^users/login/$', 'django.contrib.auth.views.login', 
        name='login'),
    url(r'^users/logout/$', 'django.contrib.auth.views.logout',
        name='logout'),
    url(r'^admin/', include(admin.site.urls)),
)
