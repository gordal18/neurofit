from django.apps import AppConfig


class CNMBConfig(AppConfig):
	name = 'cnmb'
	verbose_name = 'CNMB'

	def ready(self):
		# Register signal handlers
		from . import signals
