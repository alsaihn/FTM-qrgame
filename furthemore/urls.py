from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('game.views',
    # Examples:
    # url(r'^$', 'furthemore.views.home', name='home'),
    url(r'^$', 'index'),
    url(r'^room/$', 'roomlist'),
    url(r'^room/notfound/$', 'room_not_found'),
    url(r'^room/wait/(?P<user_id>\d+)/$', 'room_wait'),
    url(r'^room/(?P<room_id>\d+)/$', 'roomdata'),
    url(r'^room/(?P<room_id>\d+)/checkin/$', 'roomcheckin'),
    url(r'^room/(?P<room_id>\d+)/checkin/(?P<user_id>\d+)/$', 'roomcheckin_validate'),
    url(r'^room/(?P<room_id>\d+)/checkin/done/$', 'roomcheckin_done'),

    url(r'^register/(?P<badge_number>\d+)/$', 'register'),
    url(r'^register/notfound/$', 'register_not_found'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
