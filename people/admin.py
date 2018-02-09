from django.contrib import admin
from . import models


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'gender', 'location')
	
	def full_name(self, client):
		return str(client)
	full_name.admin_order_field = 'last_name'

	def location(self, client):
		return client.location()
