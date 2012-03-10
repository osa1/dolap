from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dolapapp.views.home', name='home'),
    # url(r'^dolapapp/', include('dolapapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^app/', include('dolapapp.dolap.urls')),
)

if settings.LOCAL_DEVELOPMENT:
    urlpatterns += patterns("django.views",
                            url(r"%s(?P<path>.*)/$" % settings.MEDIA_URL[1:], "static.serve",
                                 {"document_root": settings.MEDIA_ROOT}))
