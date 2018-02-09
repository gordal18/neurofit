from ckeditor.widgets import CKEditorWidget
from django import forms
from people.models import Client
from .models import CustomPage, Definition


class StartForm(forms.Form):
	defs = Definition.objects.filter(is_active=True).order_by('-date_created')
	clients = Client.objects.all()
	    
	definition = forms.ModelChoiceField(queryset=defs, empty_label=None) 
	client = forms.ModelChoiceField(queryset=clients)
	comments = forms.CharField(widget=forms.Textarea, required=False)


class EditAdministrationForm(forms.Form):
	comments = forms.CharField(widget=forms.Textarea, required=False)


class AdministrationMediaForm(forms.Form):
	media_file = forms.FileField()


class QuestionsForm(forms.Form):
	email = forms.EmailField(label='Your Email')
	message = forms.CharField(widget=forms.Textarea)


class CustomPageAdminForm(forms.ModelForm):
	content = forms.CharField(widget=CKEditorWidget(), required=False)

	class Meta:
		model = CustomPage
		exclude = ('slug',)
