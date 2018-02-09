from django.conf.urls import url
from . import views


urlpatterns = [
	url(r'^$', views.home, name='home'),
	url(r'^start/$', views.start_admin, name='start'),
	url(r'^administrations/$', views.administrations, name='admins'),
	url(r'^administration-(?P<admin_id>[0-9]+)/$', views.admin, name='admin'),
	url(r'^administration-(?P<admin_id>[0-9]+)/section-(?P<section_num>[0-9]+)/$',
		views.section, name='section'),
	url(r'^administration-(?P<admin_id>[0-9]+)/item-(?P<item_id>[0-9]+)-upload/$', views.upload, name='upload'),
	url(r'^trainers/$', views.trainers, name='trainers'),
	url(r'^trainers/(?P<username>[0-9a-zA-Z@.+_-]+)/$', views.trainer, name='trainer'),
	url(r'^client-(?P<client_id>[0-9]+)/$', views.client, name='client'),
	url(r'^client-(?P<client_id>[0-9]+)-chart/$', views.client_chart, name='client_chart'),
	url(r'^client-(?P<client_id>[0-9]+)-media/$', views.client_media, name='client_media'),
	url(r'^clients/$', views.clients, name='clients'),
	url(r'^questions/$', views.client_questions, name='questions'),
	# Catch-all -- should be last in the list of patterns:
	url(r'^(?P<slug>[a-z0-9_-]+)/$', views.custom_page, name='custom_page'),
]
