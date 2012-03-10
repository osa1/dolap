from django.conf.urls.defaults import patterns, include, url

from views import login, home, intro, logout

urlpatterns = patterns('',
    (r'^$', intro),
    (r'^home/$', home),
    (r'^login/$', login),
    (r'^logout/$', logout),
)
