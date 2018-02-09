from django import template
from cnmb.views import is_trainer as ORIG_is_trainer
from cnmb.views import is_client as ORIG_is_client


register = template.Library()


@register.filter
def user_nice(user):
	if user:
		if user.first_name or user.last_name:
			return u'%s %s' % (user.first_name, user.last_name)
		return user.username
	return u''


@register.filter
def is_trainer(user):
	return ORIG_is_trainer(user)


@register.filter
def is_client(user):
	return ORIG_is_client(user)


@register.assignment_tag
def get_nav_custom_pages(user):
	if not is_client(user):
		return # For now, only clients have custom nav pages

	from cnmb.models import CustomPage
	pages = CustomPage.objects.filter(client_viewable=True, navbar_order__gt=0).order_by('navbar_order').defer('content')
	return pages
