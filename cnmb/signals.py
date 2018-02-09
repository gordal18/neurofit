import logging
import os
from django.db import models
from django.dispatch import receiver
from .models import AdministrationMedia

logger = logging.getLogger('cnmb')


@receiver(models.signals.post_delete, sender=AdministrationMedia, dispatch_uid='cnmb_rfod')
def remove_file_on_delete(sender, instance, **kwargs):
	logger.debug('remove_file_on_delete')
	if instance.media_file and os.path.isfile(instance.media_file.path):
		os.remove(instance.media_file.path)
		logger.debug('removed "%s"', instance.media_file.path)


@receiver(models.signals.pre_save, sender=AdministrationMedia, dispatch_uid='cnmb_rfoc')
def remove_file_on_change(sender, instance, **kwargs):
	logger.debug('remove_file_on_change')

	if not instance.id:
		logger.debug('null id (new instance)')
		return

	try:
		old = AdministrationMedia.objects.get(instance.id).media_file
	except AdministrationMedia.DoesNotExist:
		logger.debug('old id doesnt exist')
		return

	if instance.media_file != old and os.path.isfile(old.path):
		os.remove(old.path)
		logger.debug('removed "%s"', old.path)
