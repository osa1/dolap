from django.conf.urls.defaults import patterns

from views import files, intro, logout, home, \
    json_login, json_edit_file, json_file_list, json_file_details, \
    json_last_added_files, json_last_updated_files, json_update_files, \
    file_details, shelf, profile, json_follow_user, json_unfollow_user

urlpatterns = patterns('',
    (r'^$', intro),
    (r'^home/$', home),
    (r'^files/$', files),
    (r'^file/(?P<file_owner>[0-9]+)/(?P<path>[A-Za-z0-9-_%/ \.]+)/$',
        file_details),
    (r'^shelf/(?P<shelf>[A-Za-z0-9- _]+)/$', shelf),
    (r'^user/(?P<uid>[0-9]+)/$', profile),

    (r'^json_login/$', json_login),
    (r'^json_file_list/$', json_file_list),
    (r'^json_edit_file/$', json_edit_file),
    (r'^json_last_updated_files/$', json_last_updated_files),
    (r'^json_last_added_files/$', json_last_added_files),
    (r'^json_update_files/$', json_update_files),
    # TODO: match %
    (r'^json_file_details/(?P<file>[A-Za-z0-9-_%/\.]+)/$', json_file_details),
    (r'^follow/(?P<uid>[0-9]+)/$', json_follow_user),
    (r'^unfollow/(?P<uid>[0-9]+)/$', json_unfollow_user),

    (r'^logout/$', logout),
)
