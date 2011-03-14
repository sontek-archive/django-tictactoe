from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TicTacToe.views.home', name='home'),
    url(r'', include('tictactoe.core.urls')),
    (r'^users/', include('registration.urls')),
    url(r'^users/login/$', 'django.contrib.auth.views.login', 
        name='login'),
    url(r'^users/logout/$', 'django.contrib.auth.views.logout',
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
