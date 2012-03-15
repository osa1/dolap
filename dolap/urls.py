from django.conf.urls.defaults import patterns, include, url

from views import login, home, intro, logout, details, json_test, json_template, \
    json_login

urlpatterns = patterns('',
    (r'^$', intro),
    (r'^home/$', home),
    (r'^login/$', login),
    (r'^json_login/$', json_login),
    (r'^logout/$', logout),
    # TODO: match %
    (r'^file/(?P<file>[A-Za-z0-9-_%/\.]+)/$', details),
    (r'^json-test/$', json_test),
    (r'^json/$', json_template),
)
