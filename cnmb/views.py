from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django.http import HttpResponseForbidden
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from people.models import Client
from people.forms import ClientForm
from .forms import StartForm, EditAdministrationForm, AdministrationMediaForm, QuestionsForm
from .models import Administration, AdministrationMedia, CustomPage, Section, Item
from .helpers import TRAINERS_GROUP, loc_name, loc_groups

import logging
logger = logging.getLogger('cnmb')


def is_valid_user(user):
	return user.is_active and user.is_authenticated()

def is_trainer(user):
	return user.groups.filter(name=TRAINERS_GROUP).exists()

def is_valid_trainer(user):
	return is_valid_user(user) and is_trainer(user)

def is_client(user):
	return Client.objects.filter(user=user).exists()

def user_client(user):
	try:
		return Client.objects.filter(user=user).get()
	except Client.DoesNotExist:
		return None


def redirect_home(request):
	return HttpResponseRedirect(reverse('cnmb:home'))

@user_passes_test(is_valid_user)
def home(request):
	if not is_trainer(request.user):
		return HttpResponseRedirect(reverse('cnmb:client', args=[0]))
	
	recents_list = Administration.objects.filter(trainer=request.user).order_by('-date_given')[:10]
	context = {'recents_list': recents_list}
	return render(request, 'cnmb/home.html', context)

@user_passes_test(is_valid_user)
def client(request, client_id):
	if is_trainer(request.user):
		client = get_object_or_404(Client, pk=client_id)
	else:
		return client_self(request)
	
	a_list = Administration.objects.filter(client=client_id).order_by('date_given')
	
	if request.method == 'POST':
		form = ClientForm(request.POST, instance=client)
		form.save()
	else:
		form = ClientForm(instance=client)

	#if client.user:
	#	loc_list = [ loc_name(g.name) for g in loc_groups(client.user) ]
	#	client.locations = ', '.join(loc_list)
	
	context = {'client': client, 'administrations': a_list, 'form': form}
	return render(request, 'cnmb/client.html', context)

@user_passes_test(is_valid_user)
def client_self(request):
	client = user_client(request.user)
	if not client: return HttpResponseForbidden()
	
	a_list = Administration.objects.filter(client=client).order_by('date_given')

	contentA = CustomPage.objects.get(pk=1).content #hardcoded
	contentB = CustomPage.objects.get(pk=2).content #hardcoded

	context = {'client': client, 'administrations': a_list, 'contentA': contentA, 'contentB': contentB}
	return render(request, 'cnmb/client.html', context)

@user_passes_test(is_valid_user)
def client_questions(request):
	client = user_client(request.user)
	if not client: return HttpResponseForbidden()
	success = False

	if request.method == 'POST':
		form = QuestionsForm(request.POST)
		if form.is_valid():
			subj = 'Questions RE: ' + str(client)
			msg = form.cleaned_data['message']
			try:
				r = send_mail(subj, msg, form.cleaned_data['email'], ['admin@neuro-fit.com'])
			except Exception as e:
				logger.warning(u'send_mail exception: %s', e)

			if r < 1:
				logger.warning(u'send_mail returned %d sending to "%s"', r, form.email)
			else:
				success = True
	else:
		form = QuestionsForm()

	context = {'form': form, 'client': client, 'success': success}
	return render(request, 'cnmb/questions.html', context)

@user_passes_test(is_valid_user)
def client_chart(request, client_id):
	contentA = ''
	if is_trainer(request.user):
		client = get_object_or_404(Client, pk=client_id)
	else:
		client = user_client(request.user)
		if not client: return HttpResponseForbidden()
		contentA = CustomPage.objects.get(pk=5).content #hardcoded

	a_list = Administration.objects.filter(client=client).order_by('date_given')
	sections = Section.objects.filter(definition=a_list[0].definition) if len(a_list) else []

	context = {'client': client, 'administrations': a_list, 'sections': sections, 'contentA': contentA}
	return render(request, 'cnmb/client_chart.html', context)

@user_passes_test(is_valid_user)
def client_media(request, client_id):
	contentA = ''
	contentB = ''
	if is_trainer(request.user):
		client = get_object_or_404(Client, pk=client_id)
	else:
		client = user_client(request.user)
		if not client: return HttpResponseForbidden()
		contentA = CustomPage.objects.get(pk=6).content #hardcoded
		contentB = CustomPage.objects.get(pk=7).content #hardcoded

	# Go through every Administration the Client has
	final_admins = []
	a_list = Administration.objects.filter(client=client)
	for a in a_list:
		sections = {}
		m_list = AdministrationMedia.objects.filter(administration=a)
		# Go through all the media for this Administration
		for m in m_list:
			item = m.item
			s = item.section
			if s in sections:
				s_items = sections[s]
				if item in s_items:
					s_items[item].append(m)
				else:
					s_items[item] = [m]
			else:
				sections[s] = {item: [m]}
		# If any media was added for this Administration
		if len(sections) > 0:
			# Save it for the final output
			final_admins.append({'administration': a, 'sections': sections})

	context = {'client': client, 'administrations': final_admins, 'contentA': contentA, 'contentB': contentB}
	return render(request, 'cnmb/client_media.html', context)

@user_passes_test(is_valid_trainer)
def clients(request):
	locations = []
	# For each location that current trainer has
	for g in loc_groups(request.user):
		# Get clients at that location
		c_list = Client.objects.filter(location_group=g)
		locations.append({'name': loc_name(g.name), 'clients': c_list})

	#OLD: Get all clients
	#c_list = Client.objects.order_by('location_group', 'last_name', 'first_name')
	#context = {'clients': c_list}

	context = {'locations': locations}
	return render(request, 'cnmb/clients.html', context)

@user_passes_test(is_valid_trainer)
def start_admin(request):
	if request.method == 'POST':
		form = StartForm(request.POST)
		if form.is_valid():
			definition = form.cleaned_data['definition']
			client = form.cleaned_data['client']
			comments = form.cleaned_data['comments']
			a = Administration(definition=definition, client=client, 
							trainer=request.user, comments=comments)
			a.save()
			return HttpResponseRedirect(reverse('cnmb:section', args=(a.pk, 1)))
	else:
		form = StartForm()
	
	return render(request, 'cnmb/start.html', {'form': form})

@user_passes_test(is_valid_trainer)
def administrations(request):
	a_list = Administration.objects.order_by('-date_given')
	context = {'administrations': a_list}
	return render(request, 'cnmb/administrations.html', context)

@user_passes_test(is_valid_user)
def admin(request, admin_id):
	a = get_object_or_404(Administration, pk=admin_id)

	contentA = ''
	contentB = ''
	trainer = is_trainer(request.user)
	if not trainer:
		client = user_client(request.user)
		if (not client) or (client.id != a.client.id):
			return HttpResponseForbidden()
		contentA = CustomPage.objects.get(pk=3).content #hardcoded
		contentB = CustomPage.objects.get(pk=4).content #hardcoded

	saved = False
	if trainer:
		if request.method == 'POST':
			form = EditAdministrationForm(request.POST)
			if form.is_valid():
				comments = form.cleaned_data['comments']
				a.comments = comments
				a.save()
				saved = True
		else:
			form = EditAdministrationForm(initial={'comments': a.comments})
	else:
		form = None
	
	sections = Section.objects.filter(definition=a.definition)
	total_score = 0
	max_score = 0
	for section in sections:
		max_score += section.max_score()
		t = a.section_score(section)
		total_score += t
		section.total_score = t  # Save for template
	
	context = {'admin': a, 'sections': sections,
			'total_score': total_score, 'max_score': max_score, 
			'form': form, 'saved': saved,
			'contentA': contentA, 'contentB': contentB}
	return render(request, 'cnmb/admin.html', context)

@user_passes_test(is_valid_trainer)
def trainers(request):
	u_list = User.objects.filter(groups__name=TRAINERS_GROUP).order_by('last_name')
	locations = {}
	unknowns = []
	for u in u_list:
		any_location = False
		for g in loc_groups(u):
			if g.name in locations:
				locations[g.name].append(u)
			else:
				locations[g.name] = [u]
			any_location = True
		if not any_location:
			unknowns.append(u)
	
	loc_list = []
	for gname in sorted(locations):
		loc_list.append({'name': loc_name(gname), 'users': locations[gname]})
	if unknowns:
		loc_list.append({'name': 'Unknown Location', 'users': unknowns})

	#context = {'users': u_list}
	context = {'locations': loc_list}
	return render(request, 'cnmb/trainers.html', context)

@user_passes_test(is_valid_trainer)
def trainer(request, username):
	u = get_object_or_404(User, username=username)
	a_list = Administration.objects.filter(trainer=u).order_by('-date_given')
	context = {'page_user': u, 'administrations': a_list}
	return render(request, 'cnmb/trainer.html', context)

def save_POST_score(a, item, score_val):
	if score_val is None: # Ignore this Item
		logger.info(u'Missing expected POST field item-%d', item.pk)
	elif not score_val: # Remove any current Score
		for s in item.sel_scores:
			logger.debug(u'Removing score-num %d for item %d', s.score, item.pk)
			a.scores.remove(s)
	else: # Remove any current Score and add new one
		try:
			score_num = int(score_val)
		except ValueError:
			logger.warning(u'Could not convert POST[item-%d]="%s" to int', item.pk, score_val)
			return
		logger.debug(u'Got score-num %d for item %d', score_num, item.pk)
		new_score = None
		for s in item.score_set.all():
			if s.score == score_num:
				new_score = s
				break
		if new_score is None:
			logger.warning(u'...score-num %d does not exist for item %d', score_num, item.pk)
			return
		for s in item.sel_scores:
			if s.score == score_num:
				logger.debug(u'...already present in Administration')
				return
			else:
				logger.debug(u'...removing score-num %d', s.score)
				a.scores.remove(s)
		logger.debug(u'...adding new score %d', score_num)
		a.scores.add(new_score)

@user_passes_test(is_valid_trainer)
def section(request, admin_id, section_num):
	section_num = int(section_num)
	a = get_object_or_404(Administration, pk=admin_id)
	section = get_object_or_404(Section, definition=a.definition, number=section_num)
	items = Item.objects.filter(section=section)
	save = request.method == 'POST'
	
	with atomic():
		for item in items:
			item.sel_scores = a.scores.filter(item=item) # Used by template too
			item.admin_media = AdministrationMedia.objects.filter(administration=a, item=item)
			if save:
				score_val = request.POST.get(u'item-%d' % item.pk)
				save_POST_score(a, item, score_val)
	
	if save:
		next_section = Section.objects.filter(definition=a.definition, number__gt=section_num).first()
		if next_section:
			logger.debug(u'next section is %d', next_section.number)
			u = reverse('cnmb:section', args=(a.pk, next_section.number))
		else:
			logger.debug(u'last section')
			u = reverse('cnmb:admin', args=(a.pk,))
		return HttpResponseRedirect(u)
	else:
		sections = Section.objects.filter(definition=a.definition)
		context = {'admin': a, 'section': section, 'sections': sections, 'items': items}
		return render(request, 'cnmb/section.html', context)

@user_passes_test(is_valid_trainer)
def upload(request, admin_id, item_id):
	a = get_object_or_404(Administration, pk=admin_id)
	item = get_object_or_404(Item, pk=item_id)
	media = AdministrationMedia.objects.filter(administration=a, item=item)
	saved = False

	if request.method == 'POST':
		form = AdministrationMediaForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				new_media = AdministrationMedia(media_file=request.FILES['media_file'], administration=a, item=item)
				new_media.save()
				saved = True
			except ValidationError as e:
				form.add_error('media_file', e)
	else:
		form = AdministrationMediaForm()

	context = {'admin': a, 'item': item, 'media': media, 'form': form, 'saved': saved}
	return render(request, 'cnmb/upload.html', context)


@user_passes_test(is_valid_user)
def custom_page(request, slug):
	page = get_object_or_404(CustomPage, slug=slug)

	if not page.client_viewable and is_client(request.user):
		return HttpResponseForbidden()

	context = {'page': page}
	return render(request, 'cnmb/custom_page.html', context)
