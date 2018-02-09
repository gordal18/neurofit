from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import localtime, now as tz_now
from people.models import Client

import logging
import os.path
from __builtin__ import classmethod
logger = logging.getLogger('cnmb')


# The definition of a CNMB that is administered to clients.
class Definition(models.Model):
	title = models.CharField(max_length=255)
	edition = models.CharField(max_length=255, blank=True)
	short_name = models.CharField(max_length=31, blank=True)
	date_created = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=False, blank=True)

	class Meta:
		ordering = ('date_created',)

	def __unicode__(self):
		return self.short_name or (u'CNMB (%s)' % 
									(self.edition or localtime(self.date_created).date()))
	
	@classmethod
	def deep_copy(cls, d):
		old_pk = d.pk
		d.pk = None
		d.is_active = False
		d.short_name += u' copy'
		d.save()
		logger.debug('deep-copied Definition %d', old_pk)
		Section.deep_copy(old_pk, d.pk)


# A section of a Definition.
class Section(models.Model):
	definition = models.ForeignKey(Definition)
	number = models.IntegerField()
	title = models.CharField(max_length=255)

	class Meta:
		ordering = ('-definition', 'number')
		unique_together = ('definition', 'number')

	def __unicode__(self):
		return u'[%s] %s' % (self.definition, self.title)
	
	def max_score(self):
		val = getattr(self, 'cached_max_score', None)
		if val is None:
			val = sum(item.max_score() for item in self.item_set.all())
			self.cached_max_score = val
		return val
	
	@classmethod
	def deep_copy(cls, old_def_pk, new_def_pk):
		sections = Section.objects.filter(definition=old_def_pk)
		for s in sections:
			old_pk = s.pk
			s.pk = None
			s.definition = Definition(pk=new_def_pk)
			s.save()
			Item.deep_copy(old_pk, s.pk)
		logger.debug('  deep-copied %d Sections', len(sections))



# An exercise item within a Section.
class Item(models.Model):
	section = models.ForeignKey(Section)
	number = models.IntegerField()
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ('section', 'number',)
		unique_together = ('section', 'number')

	def __unicode__(self):
		return self.name
	
	def max_score(self):
		return self.score_set.aggregate(models.Max('score'))['score__max']

	@classmethod
	def deep_copy(cls, old_sec_pk, new_sec_pk):
		items = Item.objects.filter(section=old_sec_pk)
		for item in items:
			old_pk = item.pk
			item.pk = None
			item.section = Section(pk=new_sec_pk)
			item.save()
			Score.deep_copy(old_pk, item.pk)
		logger.debug('    deep-copied %d Items', len(items))


# A possible score for an Item.
class Score(models.Model):
	item = models.ForeignKey(Item)
	score = models.IntegerField()
	description = models.TextField(blank=True)

	class Meta:
		ordering = ('item', '-score')

	def __unicode__(self):
		return u'[%s] %s' % (self.score, self.description)
	
	@classmethod
	def deep_copy(cls, old_item_pk, new_item_pk):
		scores = Score.objects.filter(item=old_item_pk)
		for score in scores:
			score.pk = None
			score.item = Item(pk=new_item_pk)
			score.save()
		logger.debug('      deep-copied %d Scores', len(scores))


# An administration of a Definition to a Client.
class Administration(models.Model):
	definition = models.ForeignKey(Definition)
	client = models.ForeignKey(Client)
	trainer = models.ForeignKey(User)
	date_given = models.DateTimeField(default=tz_now)
	comments = models.TextField(blank=True)
	scores = models.ManyToManyField(Score, blank=True)

	class Meta:
		ordering = ('date_given',)

	def __unicode__(self):
		return u'%s (%s)' % (self.client, localtime(self.date_given).date())
	
	def section_score(self, section):
		"""The total score for the given Section"""
		if section.definition != self.definition:
			raise ValueError(u'section is not from the right Definition')
		d = self.scores.filter(item__section=section).aggregate(models.Sum('score'))
		return d['score__sum'] or 0

	def total_score(self):
		"""The total score for the entire Administration"""
		d = self.scores.aggregate(models.Sum('score'))
		return d['score__sum'] or 0

	def section_scores(self):
		"""A list of (score,max) tuples for each Section"""
		sections = Section.objects.filter(definition=self.definition)
		return [ (self.section_score(s), s.max_score()) for s in sections ]


# Media-file directory relative to MEDIA_ROOT
ALLOWED_EXTS = ['bmp', 'gif', 'jpeg', 'jpg', 'png', 'mp4', 'm4v', 'mov']
def media_path(instance, filename):
	f, e = os.path.splitext(filename)
	e = e[1:].lower()
	if e not in ALLOWED_EXTS:
		from django.core.exceptions import ValidationError
		raise ValidationError(u'Invalid file extension "%(ext)s". Must be image (e.g. JPG) or video (e.g. MP4).', code='invalid_ext', params={'ext': e.upper()})
	return u'cnmb/administration-%d/%s.%s' % (instance.administration.id, f, e)

# A media file associated with an Item for a particular Administration
class AdministrationMedia(models.Model):
	media_file = models.FileField(upload_to=media_path)
	administration = models.ForeignKey(Administration)
	item = models.ForeignKey(Item)

	class Meta:
		ordering = ('administration', 'item')
		verbose_name_plural = 'administration media'

	def __unicode__(self):
		return u'%s - %s' % (self.administration, self.item)

	def filename(self):
		return os.path.basename(self.media_file.url)


# Custom page created and editable by users
class CustomPage(models.Model):
	title = models.CharField(max_length=255)
	slug = models.CharField(max_length=255, blank=True)
	last_modified = models.DateTimeField(auto_now=True)
	content = models.TextField(blank=True)

	client_viewable = models.BooleanField(default=False, blank=True)
	navbar_order = models.IntegerField(default=0, blank=True) # lte 0 means not shown

	class Meta:
		ordering = ('title',)

	def __unicode__(self):
		return self.title

	def save(self, *args, **kwargs):
		from django.template.defaultfilters import slugify
		self.slug = slugify(self.title)
		super(CustomPage, self).save(*args, **kwargs)
