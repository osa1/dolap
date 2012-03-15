from django.conf.urls.defaults import patterns, include, url

from views import user_home, intro, logout, details, \
    json_login, json_edit_file, json_file_list

urlpatterns = patterns('',
    (r'^$', intro),
    (r'^home/$', user_home),
    # (r'^login/$', login),
    # (r'^list/$', ),
    (r'^json_login/$', json_login),
    (r'^json_file_list/$', json_file_list),
    (r'^json_edit_file/$', json_edit_file),
    (r'^logout/$', logout),
    # TODO: match %
    (r'^file/(?P<file>[A-Za-z0-9-_%/\.]+)/$', details),
)
