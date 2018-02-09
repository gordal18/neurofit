#from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse as reverse_url
from django.db.transaction import atomic
from django.utils.html import format_html
#from django.utils.http import urlencode
from . import forms, models
from __builtin__ import False


# Decorator for convenience
def short_desc(desc):
	def deco(f):
		f.short_description = desc
		return f
	return deco


class ScoreInline(admin.TabularInline):
	model = models.Score
	extra = 1


class ItemInline(admin.TabularInline):
	model = models.Item
	extra = 1
	exclude = ('description',)
	readonly_fields = ('edit_link',)
	
	@short_desc(u'Edit')
	def edit_link(self, item):
		if item.pk:
			u = reverse_url('admin:cnmb_item_change', args=(item.pk,))
			return format_html(u'<a href="{}">Edit Description and Scores</a>', u)
		else:
			return ''
	#edit_link.short_description = u'Edit'


@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
	inlines = [ScoreInline]
	save_as = True
	exclude = ('section',)
	readonly_fields = ('section_link',)
	list_display = ('name', 'number', 'section')
	list_filter = ('section',)
	preserve_filters = True
	
	@short_desc(u'Section')
	def section_link(self, item):
		if not item.pk: return u''
		u = reverse_url('admin:cnmb_section_change', args=(item.section.pk,))
		return format_html(u'<a href="{}">{}</a>', u, item.section)
	#section_link.short_description = u'Section'
	
	#def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
	#	if db_field == 'section':
	#		kwargs['queryset'] = models.Section.objects.filter(definition='TODO!')
	#	return super(ItemAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class SectionInline(admin.TabularInline):
	model = models.Section
	extra = 1
	readonly_fields = ('items_link',)
	
	@short_desc(u'Items')
	def items_link(self, section):
		if section.pk:
			n = section.item_set.count()
			#u = reverse_url('admin:cnmb_item_changelist') + \
			#	'?' + urlencode((('section__id__exact', section.pk),))
			u = reverse_url('admin:cnmb_section_change', args=(section.pk,))
			return format_html(u'<a href="{}">{} item{}</a>', u, n, ('' if n == 1 else 's'))
		else:
			return u''
	#items_link.short_description = 'Items' 


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
	inlines = [ItemInline]
	exclude = ('definition',)
	readonly_fields = ('definition_link',)
	list_filter = ('definition',)
	list_display = ('title', 'number')
	preserve_filters = True
	
	@short_desc(u'Definition')
	def definition_link(self, section):
		if not section.pk: return u''
		u = reverse_url('admin:cnmb_definition_change', args=(section.definition.pk,))
		return format_html(u'<a href="{}">{}</a>', u, section.definition)
	#definition_link.short_description = u'Definition'


@admin.register(models.Definition)
class DefinitionAdmin(admin.ModelAdmin):
	inlines = [SectionInline]
	list_display = ('short_name', 'edition', 'title', 'is_active')
	list_display_links = ('short_name', 'title')
	actions = ['deep_copy_definitions']
	
	@atomic
	@short_desc(u'Copy selected definitions')
	def deep_copy_definitions(self, request, qset):
		for d in qset:
			models.Definition.deep_copy(d)
		n = len(qset)
		if n == 1: msg = u'Created a copy "%s".' % qset[0]
		else:      msg = u'%d CNMB definitions have been copied' % n
		self.message_user(request, msg)		


# class AdministrationAdminForm(forms.ModelForm):
# 	def clean(self):
# 		super(AdministrationAdminForm, self).clean()
# 		scores = self.cleaned_data.get('scores')
# 		if scores:
# 			msg = 'This score is not from the correct CNMB definition: "%s"'
# 			item2scores = {}
# 			from django.core.exceptions import ValidationError
# 			for score in scores:
# 				# Ensure score is from the correct Definition
# 				if score.item.section.definition != self.instance.definition:
# 					self.add_error('scores', ValidationError(msg, params=(score,)))
# 				# Ensure score is the only one from its Item
# 				item_scores = item2scores.get(score.item.pk)
# 				if item_scores:
# 					item_scores.append(score)
# 				else:
# 					item2scores[score.item.pk] = [score]
# 			msg2 = 'These are all from the same CNMB item: %s'
# 			for scores_list in item2scores.values():
# 				if len(scores_list) > 1:
# 					self.add_error('scores', ValidationError(msg2, params=(scores_list,)))


@admin.register(models.Administration)
class AdministrationAdmin(admin.ModelAdmin):
	exclude = ('scores',)
	readonly_fields = ('definition',)
	list_display = ('client', 'date_given')
	list_display_links = ('client', 'date_given')
	#filter_vertical = ('scores',)
	#form = AdministrationAdminForm


@admin.register(models.AdministrationMedia)
class AdministrationMediaAdmin(admin.ModelAdmin):
	list_display = ('media_file', 'administration', 'item')


@admin.register(models.CustomPage)
class CustomPageAdmin(admin.ModelAdmin):
	exclude = ('slug',)
	list_display = ('title',)
	form = forms.CustomPageAdminForm
