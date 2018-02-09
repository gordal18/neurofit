from cnmb.helpers import is_loc, loc_name
from django.contrib.auth.models import User, Group
from django.db import models


class Client(models.Model):
	first_name = models.CharField(max_length=127)
	last_name = models.CharField(max_length=127)
	FEMALE, MALE = ('F', 'M')
	GENDERS = ((FEMALE, 'female'), (MALE, 'male'))
	gender = models.CharField(choices=GENDERS, max_length=1, blank=True)
	# Setting null below because blank doesn't work, it's not a string.
	birthday = models.DateField(null=True, blank=True)
	parent = models.CharField(max_length=255, blank=True)
	email = models.EmailField(blank=True)
	phone = models.CharField(max_length=31, blank=True)
	comments = models.TextField(blank=True)
	# Client can optionally have a user account.
	user = models.OneToOneField(User, blank=True, null=True, on_delete=models.SET_NULL)
	# Group representing location
	location_group = models.ForeignKey(Group, blank=True, null=True)
	
	class Meta:
		ordering = ('last_name', 'first_name')

	def __unicode__(self):
		return u'%s %s' % (self.first_name, self.last_name)

	# Convenience method to get location name
	def location(self):
		if self.location_group:
			name = self.location_group.name
			if is_loc(name):
				return loc_name(name)
			return name
		return u''
