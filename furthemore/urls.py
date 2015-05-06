from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('game.views',
    # Examples:
    # url(r'^$', 'furthemore.views.home', name='home'),
    url(r'^$', 'index'),
    url(r'^group/$', 'grouplist'),
    url(r'^group/notfound/$', 'group_not_found'),
    url(r'^group/(?P<group_id>\d+)/$', 'groupdata'),

	url(r'^panel/(?P<panel_id>\d+)/checkin/$', 'panelcheckin'),
    
    url(r'^qr/notfound/$', 'qr_not_found'),
    url(r'^qr/wait/(?P<user_id>\d+)/$', 'qr_wait'),
    url(r'^qr/(?P<qr_id>\d+)/checkin/$', 'qrcheckin'),
    url(r'^qr/(?P<qr_id>\d+)/checkin/(?P<user_id>\d+)/$', 'qrcheckin_validate'),
    url(r'^qr/(?P<qr_id>\d+)/checkin/done/$', 'qrcheckin_done'),

	url(r'^qr/generate/$', 'qrgenerate'),

    url(r'^register/(?P<badge_number>\d+)/$', 'register'),
    url(r'^register/notfound/$', 'register_not_found'),

    url(r'^statistics', 'get_statistics'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
