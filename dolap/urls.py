from django.conf.urls.defaults import patterns, include, url

from views import login, home, intro, logout, details

urlpatterns = patterns('',
    (r'^$', intro),
    (r'^home/$', home),
    (r'^login/$', login),
    (r'^logout/$', logout),
    # TODO: match %
    (r'^file/(?P<file>[A-Za-z0-9-_%/\.]+)/$', details),
)
