from django.conf.urls import include, url
from django.contrib.admin import site as admin_site
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
#from django.contrib.sites.models import Site


admin_site.site_header = 'Neuro-fit Admin'
admin_site.site_title = 'Neuro-fit Admin'
admin_site.site_url = 'http://138.68.244.70/'#' + Site.objects.get_current().domain
admin_site.index_title = ''

def auth_url(name, extra_path=''):
	path = r'^%s%s/$' % (name, extra_path)
	view = getattr(auth_views, name)
	context = {'template_name': 'auth/%s.html' % name}
	if name == 'password_reset':
		context['email_template_name'] = 'auth/password_reset_email.txt'
		context['subject_template_name'] = 'auth/password_reset_subject.txt'
	return url(path, view, context, name=name)

auth_patterns = [
	auth_url('login'),
	auth_url('logout'),
	auth_url('password_reset'),
	auth_url('password_reset_done'),
	auth_url('password_reset_confirm',
			r'/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})'),
	auth_url('password_reset_complete'),
	auth_url('password_change'),
	auth_url('password_change_done'),
]

urlpatterns = [
	url(r'^$', 'cnmb.views.redirect_home'),

	url(r'^admin/', include(admin_site.urls)),

	url(r'^cnmb/', include('cnmb.urls', namespace='cnmb')),
	
	url(r'^auth/', include(auth_patterns)),

	url(r'^ckeditor/', include('ckeditor_uploader.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
