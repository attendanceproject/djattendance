# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import json
import re

from accounts.models import Trainee
from aputils.decorators import group_required
from aputils.trainee_utils import is_trainee, trainee_from_user
from braces.views import GroupRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q, Case, When
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from .constants import DESTINATION_FIELDS
from .forms import (AnswerForm, GospelTripForm, LocalImageForm, NonTraineeForm,
                    SectionFormSet)
from .models import (Answer, Destination, GospelTrip, NonTrainee, Question,
                     Section)
from .nontrainee import ApplicationForm, FlightFormSet, PassportForm
from .utils import (export_to_json, get_airline_codes, get_airport_codes,
                    import_from_json, section_order_validator)


class GospelTripView(GroupRequiredMixin, CreateView):
  model = GospelTrip
  template_name = 'gospel_trips/gospel_trips_admin.html'
  form_class = GospelTripForm
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    ctx = super(GospelTripView, self).get_context_data(**kwargs)
    ctx['gospel_trips'] = GospelTrip.objects.order_by('-open_time')
    ctx['page_title'] = 'Gospel Trip Admin'
    return ctx


@group_required(['training_assistant'])
def gospel_trip_admin_update(request, pk):
  gt = get_object_or_404(GospelTrip, pk=pk)
  context = {'page_title': 'Gospel Trip Editor'}
  data = request.POST

  if request.method == "POST":
    form_set = SectionFormSet(data, instance=gt)
    form = GospelTripForm(data, instance=gt)

    if form.is_valid() and form_set.is_valid():
      form.save()
      form_set.save()

      gt_u = GospelTrip.objects.get(pk=pk)
      nk = gt_u.section_set.last().pk
      gt_u.set_section_order(section_order_validator(data, nk))
      return HttpResponseRedirect("")
    else:
      context['section_formset'] = form_set
      context['gt_form'] = form
  else:
    context['section_formset'] = SectionFormSet(instance=gt)
    context['gt_form'] = GospelTripForm(instance=gt)
  return render(request, 'gospel_trips/gospel_trips_admin_update.html', context=context)


@group_required(['training_assistant'])
def gospel_trip_admin_delete(request, pk):
  gt = get_object_or_404(GospelTrip, pk=pk)
  if request.is_ajax and request.method == "DELETE":
    gt.delete()
  return JsonResponse({'success': True})


@group_required(['training_assistant'])
def gospel_trip_admin_duplicate(request, pk):
  gt = get_object_or_404(GospelTrip, pk=pk)
  path = export_to_json(gt)
  import_from_json(path)
  return redirect('gospel_trips:admin-create')


def gospel_trip_base(request):
  admin_pk = next((gt.pk for gt in GospelTrip.objects.order_by('-open_time') if gt.is_open), 0)
  if admin_pk:  # is_open is True
    return HttpResponseRedirect(reverse('gospel_trips:gospel-trip', kwargs={'pk': admin_pk}))
  else:
    admin_pk = next((gt.pk for gt in GospelTrip.objects.order_by('-open_time') if gt.keep_open), 0)
    if admin_pk:  # keep_open is True
      return HttpResponseRedirect(reverse('gospel_trips:gospel-trip', kwargs={'pk': admin_pk}))
  return HttpResponseRedirect("/")


def rosters_base(request):
  admin_pk = next((gt.pk for gt in GospelTrip.objects.order_by('-open_time') if gt.show_teams), 0)
  if admin_pk:  # is_open is True
    return HttpResponseRedirect(reverse('gospel_trips:rosters-all', kwargs={'pk': admin_pk}))
  return HttpResponseRedirect("/")


def gospel_trip_trainee(request, pk):
  gt = get_object_or_404(GospelTrip, pk=pk)
  context = {'page_title': gt.name}

  if is_trainee(request.user):
    trainee = trainee_from_user(request.user)
  else:
    context['preview_trainees'] = Trainee.objects.all()
    trainee = Trainee.objects.get(id=request.GET.get('trainee', Trainee.objects.first().id))
    context['selected_trainee'] = trainee

  section_qs = Section.objects.filter(Q(gospel_trip=gt) & ~Q(show='HIDE'))
  question_qs = Question.objects.filter(Q(section__in=section_qs) & ~Q(answer_type="None"))
  answer_forms = []
  if request.method == "POST":
    for q in question_qs:
      answer = Answer.objects.get_or_create(trainee=trainee, gospel_trip=gt, question=q)[0]
      answer_forms.append(
        AnswerForm(request.POST, prefix=q.id, instance=answer, gospel_trip__pk=pk)
      )
    if all(f.is_valid() for f in answer_forms):
      for f in answer_forms:
        answer = f.save(commit=False)
        answer.gospel_trip = gt
        answer.trainee = trainee
        answer.question = Question.objects.get(id=f.prefix)
        answer.save()
      return HttpResponseRedirect(pk)
    else:
      context['answer_forms'] = answer_forms
  else:
    for q in question_qs:
      answer = Answer.objects.get_or_create(trainee=trainee, gospel_trip=gt, question=q)[0]
      answer_forms.append(AnswerForm(prefix=q.id, instance=answer, gospel_trip__pk=pk))
    context['answer_forms'] = answer_forms

  context['section_qs'] = section_qs
  context['pk'] = gt.id
  context['AIRPORT_CODES'] = json.dumps(get_airport_codes())
  context['AIRLINE_CODES'] = json.dumps(get_airline_codes())
  return render(request, 'gospel_trips/gospel_trips.html', context=context)


class NonTraineeView(GroupRequiredMixin, TemplateView):
  template_name = 'gospel_trips/nontrainee_form.html'
  group_required = ['training_assistant']

  def post(self, request, *args, **kwargs):
    gt = get_object_or_404(GospelTrip, pk=self.kwargs['pk'])
    data = request.POST
    application_form = ApplicationForm(data, gospel_trip__pk=gt.pk)
    passport_form = PassportForm(data)
    flight_formset = FlightFormSet(data)

    ntpk = self.kwargs.get('ntpk', None)
    if ntpk:
      nt = get_object_or_404(NonTrainee, pk=ntpk)
      nontrainees_form = NonTraineeForm(instance=nt, data=data)
    else:
      nontrainees_form = NonTraineeForm(data=data)

    if nontrainees_form.is_valid():
      non_trainee = nontrainees_form.save(commit=False)
      non_trainee.gospel_trip = gt
      forms = [application_form, passport_form, flight_formset]
      if all(f.is_valid() for f in forms):
        d = {'application': application_form.cleaned_data}
        d['passport'] = passport_form.cleaned_data
        d['flights'] = []
        for f in flight_formset:
          if f.cleaned_data and f.cleaned_data['flight_type']:
            d['flights'].append(f.cleaned_data)
        non_trainee.application_data = d
        non_trainee.save()

    context = self.get_context_data()
    return super(NonTraineeView, self).render_to_response(context)

  def get_context_data(self, **kwargs):
    ctx = super(NonTraineeView, self).get_context_data(**kwargs)
    gt = get_object_or_404(GospelTrip, pk=self.kwargs['pk'])
    ntpk = self.kwargs.get('ntpk', None)
    if ntpk:
      nt = get_object_or_404(NonTrainee, pk=ntpk)
      data = nt.application_data
      ctx['application_form'] = ApplicationForm(initial=eval(data.get('application', '{}')), gospel_trip__pk=gt.pk)
      ctx['nontrainee_form'] = NonTraineeForm(instance=nt)
      ctx['passport_form'] = PassportForm(initial=eval(data.get('passport', '{}')))
      ctx['flight_formset'] = FlightFormSet(initial=eval(data.get('flights', '{}')))
    else:
      ctx['application_form'] = ApplicationForm(gospel_trip__pk=gt.pk)
      ctx['nontrainee_form'] = NonTraineeForm()
      ctx['passport_form'] = PassportForm()
      ctx['flight_formset'] = FlightFormSet()
    ctx['nontrainees'] = NonTrainee.objects.filter(gospel_trip=gt)
    return ctx


class NonTraineeReportView(GroupRequiredMixin, TemplateView):
  template_name = 'gospel_trips/non_trainee_report.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    ctx = super(NonTraineeReportView, self).get_context_data(**kwargs)
    gt = get_object_or_404(GospelTrip, pk=self.kwargs['pk'])
    nontrainees = NonTrainee.objects.filter(gospel_trip=gt)
    decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
    for ntr in nontrainees:
      data = ntr.application_data
      app_data = eval(data.get('application', '{}'))
      d = decoder.decode(json.dumps(app_data))
      for k, v in d.items():
        if 'destination' in k and bool(v):
          d[k] = Destination.objects.get(pk=v).name

      ntr.application = d
      passport_data = eval(data.get('passport', "{}"))
      ntr.passport = decoder.decode(json.dumps(passport_data))
      flight_data = eval(data.get('flights', '{}'))
      ntr.flights = decoder.decode(json.dumps(flight_data))
    ctx['nontrainees'] = nontrainees
    return ctx


class GospelTripReportView(GroupRequiredMixin, TemplateView):
  template_name = 'gospel_trips/gospel_trip_report.html'
  group_required = ['training_assistant']

  @staticmethod
  def get_trainee_dict(gospel_trip, question_qs, general_items):
    data = []
    prefetch = ['trainees']
    prefetch.extend([item for item in general_items if item in DESTINATION_FIELDS])
    destination_qs = Destination.objects.filter(gospel_trip=gospel_trip).prefetch_related(*prefetch)

    contacts = f_coords = m_coords = s_coords = []
    if 'trainee_contacts' in general_items:
      contacts = destination_qs.values_list('trainee_contacts', flat=True)
    if 'finance_coords' in general_items:
      f_coords = destination_qs.values_list('finance_coords', flat=True)
    if 'media_coords' in general_items:
      m_coords = destination_qs.values_list('media_coords', flat=True)
    if 'stat_coords' in general_items:
      s_coords = destination_qs.values_list('stat_coords', flat=True)

    destination_names = destination_qs.values('name')
    get_these_trainees = Trainee.objects.filter(Q(id__in=gospel_trip.get_submitted_trainees()))
    for t in get_these_trainees:
      ID = t.id
      entry = {
          'name': t.full_name,
          'id': ID,
          'destination': destination_qs.filter(trainees=t).first(),
          'responses': []}
      responses = question_qs.filter(answer__trainee=t).values('answer_type', 'answer__response')
      for r in responses:
        if r['answer_type'] == 'destinations' and r['answer__response']:
          try:
            r['answer__response'] = destination_names.get(id=r['answer__response'])['name']
          except ObjectDoesNotExist:
            r['answer__response'] = "Destination Does Not Exist"
      entry['responses'] = responses

      if general_items:
        if contacts:
          entry['trainee_contacts'] = "Yes" if ID in contacts else ""
        if f_coords:
          entry['finance_coords'] = "Yes" if ID in f_coords else ""
        if m_coords:
          entry['media_coords'] = "Yes" if ID in m_coords else ""
        if s_coords:
          entry['stat_coords'] = "Yes" if ID in s_coords else ""
        if 'term' in general_items:
          entry['term'] = t.current_term
        if 'gender' in general_items:
          entry['gender'] = t.gender
        if 'birthdate' in general_items:
          entry['birthdate'] = t.date_of_birth
        if 'email' in general_items:
          entry['email'] = t.email
        if 'locality' in general_items:
          entry['locality'] = t.locality
        if 'phone' in general_items:
          entry['phone'] = t.meta.phone
      data.append(entry)
    return data

  def get_context_data(self, **kwargs):
    ctx = super(GospelTripReportView, self).get_context_data(**kwargs)
    gt = GospelTrip.objects.get(pk=self.kwargs['pk'])
    question_qs = Question.objects.filter(section__gospel_trip=gt).exclude(answer_type="None")
    sections_to_show = Section.objects.filter(id__in=question_qs.values_list('section'))

    questions = self.request.GET.getlist('questions', [0])
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(questions)])
    question_qs = question_qs.filter(id__in=questions).order_by(preserved)

    general = self.request.GET.getlist('general', [])

    general_options = collections.OrderedDict([
      ('trainee_contacts', 'Trainee Contact'),
      ('finance_coords', 'Finance Coord'),
      ('media_coords', 'Media Coord'),
      ('stat_coords', 'Stats Coord'),
      ('term', 'Term'),
      ('gender', 'Gender'),
      ('locality', 'Locality'),
      ('phone', 'Phone'),
      ('email', 'Email'),
      ('birthdate', 'Birthdate')

    ])

    ctx['questions'] = question_qs
    ctx['chosen'] = question_qs.values_list('id', flat=True)
    ctx['chosen_general'] = general
    ctx['general_options'] = general_options
    ctx['sections'] = sections_to_show
    ctx['trainees'] = self.get_trainee_dict(gt, question_qs, general)
    ctx['page_title'] = 'Gospel Trip Response Report'
    return ctx


class DestinationEditorView(GroupRequiredMixin, TemplateView):
  template_name = 'gospel_trips/destination_editor.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    context = super(DestinationEditorView, self).get_context_data(**kwargs)
    gt = get_object_or_404(GospelTrip, pk=self.kwargs['pk'])
    context['page_title'] = 'Destination Editor'
    context['destinations'] = Destination.objects.filter(gospel_trip=gt)
    return context


class DestinationByPreferenceView(GroupRequiredMixin, TemplateView):
  template_name = 'gospel_trips/by_preference.html'
  group_required = ['training_assistant']

  @staticmethod
  def get_trainee_dict(gospel_trip):
    data = []
    destination_qs = Destination.objects.filter(gospel_trip=gospel_trip).prefetch_related(*DESTINATION_FIELDS)
    dest_dict = destination_qs.values('id', 'name', 'trainee_contacts')
    contacts = destination_qs.values_list('trainee_contacts', flat=True)
    f_coords = destination_qs.values_list('finance_coords', flat=True)
    m_coords = destination_qs.values_list('media_coords', flat=True)
    s_coords = destination_qs.values_list('stat_coords', flat=True)
    qs = Trainee.objects.filter(id__in=gospel_trip.get_submitted_trainees()).select_related('locality__city').prefetch_related('trainee_contacts', 'destination')
    all_answers = gospel_trip.answer_set.filter(question__label__startswith='Destination Preference').values('response', 'question__label')
    for t in qs:
      ID = t.id
      answer_set = all_answers.filter(trainee=t)
      data.append({
        'id': ID,
        'name': t.full_name,
        'term': t.current_term,
        'locality': t.locality.city.name,
        'destination': 0,
        'trainee_contact': ID in contacts,
        'finance_coord': ID in f_coords,
        'media_coord': ID in m_coords,
        'stat_coord': ID in s_coords
      })
      dest = dest_dict.filter(trainees__in=[t])
      if dest.exists():
        data[-1]['destination'] = dest.first()['id']
      for a in answer_set:
        if re.match(r'^Destination Preference \d+$', a['question__label']):  # returns None if no match
          if a['response']:
            key = "preference_" + a['question__label'].split(" ")[-1]
            try:
              data[-1][key] = dest_dict.get(id=a['response'])['name']
            except ObjectDoesNotExist:
              data[-1][key] = "Destination Does Not Exist"

    return data

  def get_context_data(self, **kwargs):
    context = super(DestinationByPreferenceView, self).get_context_data(**kwargs)
    gt = get_object_or_404(GospelTrip, pk=self.kwargs['pk'])
    dest_choices = [{'id': 0, 'name': ''}]
    dest_choices.extend([d for d in Destination.objects.filter(gospel_trip=gt).values('id', 'name')])
    context['destinations'] = dest_choices
    context['by_preference'] = self.get_trainee_dict(gt)
    context['page_title'] = 'Destination By Preference'
    return context


class DestinationByGroupView(GroupRequiredMixin, TemplateView):
  template_name = 'gospel_trips/by_group.html'
  group_required = ['training_assistant']

  def post(self, request, *args, **kwargs):
    trainee_ids = request.POST.getlist('choose_trainees', [])
    dest_id = request.POST.get('destination', 0)
    if dest_id:
      dest = Destination.objects.get(id=dest_id)
      new_set = Trainee.objects.filter(id__in=trainee_ids)
      dest.trainees.set(new_set)
      dest.save()
    context = self.get_context_data()
    return super(DestinationByGroupView, self).render_to_response(context)

  def get_context_data(self, **kwargs):
    context = super(DestinationByGroupView, self).get_context_data(**kwargs)
    gt = get_object_or_404(GospelTrip, pk=self.kwargs['pk'])
    all_destinations = Destination.objects.filter(gospel_trip=gt)
    if all_destinations.exists():
      if self.request.method == 'POST':
        destination = self.request.POST.get('destination', all_destinations.first().id)
      else:
        destination = self.request.GET.get('destination', all_destinations.first().id)
      dest = Destination.objects.get(id=destination)
      to_exclude = all_destinations.filter(~Q(trainees=None), ~Q(id=dest.id))
      context['chosen'] = dest.trainees.values_list('id', flat=True)
      context['choose_from'] = Trainee.objects.filter(id__in=gt.get_submitted_trainees()).exclude(id__in=to_exclude.values_list('trainees__id'))
      context['unassigned'] = Trainee.objects.filter(id__in=gt.get_submitted_trainees()).filter(Q(destination=None))
      if 'destinit' not in context:
        context['destinit'] = dest.id
      context['all_destinations'] = all_destinations
    else:
      context['no_destinations'] = True

    context['page_title'] = 'Destination By Group'
    context['post_url'] = reverse('gospel_trips:by-group', kwargs={'pk': gt.id})
    return context


class RostersAllTeamsView(TemplateView):
  template_name = 'gospel_trips/rosters_all_teams.html'

  @staticmethod
  def get_trainee_dict(gospel_trip, destination_qs):
    data = []
    contacts = destination_qs.values_list('trainee_contacts', flat=True)
    for t in Trainee.objects.filter(id__in=gospel_trip.get_submitted_trainees()):
      data.append({
        'name': t.full_name,
        'id': t.id,
        'trainee_contact': t.id in contacts,
        'destination': destination_qs.filter(trainees=t).first()
      })
    return data

  def get_context_data(self, **kwargs):
    context = super(RostersAllTeamsView, self).get_context_data(**kwargs)
    gt = get_object_or_404(GospelTrip, pk=self.kwargs['pk'])
    all_destinations = Destination.objects.filter(gospel_trip=gt)
    if is_trainee(self.request.user) and all_destinations.filter(trainees=self.request.user).exists():
      context['destination'] = all_destinations.get(trainees=self.request.user)
      context['page_title'] = context['destination'].name
    if self.request.user.has_group(['training_assistant']):
      context['trainees'] = self.get_trainee_dict(gt, all_destinations)
      context['page_title'] = "Rosters: All Teams"
    return context


class RostersIndividualTeamView(GroupRequiredMixin, TemplateView):
  template_name = 'gospel_trips/rosters_individual_team.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    context = super(RostersIndividualTeamView, self).get_context_data(**kwargs)
    gt = get_object_or_404(GospelTrip, pk=self.kwargs['pk'])
    all_destinations = Destination.objects.filter(gospel_trip=gt)
    destinations = self.request.GET.getlist('destinations', [])
    chosen_destinations = all_destinations.filter(id__in=destinations)
    context['all_destinations'] = all_destinations
    context['destinations'] = chosen_destinations
    context['chosen'] = chosen_destinations.values_list('id', flat=True)
    context['page_title'] = "Rosters: Individual Teams"
    return context


@group_required(['training_assistant'])
def destination_add(request, pk):
  gt = get_object_or_404(GospelTrip, pk=pk)
  if request.method == "POST":
    name = request.POST.get('destination_name', None)
    if name:
      Destination.objects.get_or_create(gospel_trip=gt, name=name)
  return redirect('gospel_trips:destination-editor', pk=pk)


@group_required(['training_assistant'])
def destination_remove(request, pk):
  get_object_or_404(GospelTrip, pk=pk)
  if request.method == "POST":
    destinations = request.POST.getlist('destinations', [])
    if destinations:
      to_remove = Destination.objects.filter(id__in=destinations)
      to_remove.delete()
  return redirect('gospel_trips:destination-editor', pk=pk)


@group_required(['training_assistant'])
def destination_edit(request, pk):
  get_object_or_404(GospelTrip, pk=pk)
  if request.method == "POST":
    destination = request.POST.get('destination', None)
    name = request.POST.get('destination_edit', None)
    if name and destination:
      obj = get_object_or_404(Destination, pk=destination)
      obj.name = name
      obj.save()
  return redirect('gospel_trips:destination-editor', pk=pk)


@group_required(['training_assistant'])
def assign_destination(request, pk):
  if request.is_ajax() and request.method == "POST":
    dest_id = request.POST.get('destination_id', 0)
    trainee_id = request.POST.get('trainee_id', 0)
    is_contact = request.POST.get('is_contact', 'false') == 'true'
    try:
      tr = Trainee.objects.get(id=trainee_id)
      gt = GospelTrip.objects.get(id=pk)
      old_dests = tr.destination.filter(gospel_trip=gt)
      if old_dests.exists():
        # Even if dest_id is 0, trainee is still removed
        old_dest = old_dests.first()
        old_dest.remove_trainee(tr)
      new_dest = Destination.objects.get(id=dest_id)
      new_dest.trainees.add(tr)
      new_dest.save()
      new_dest.set_trainee_as(tr, 'trainee_contacts',set_to=is_contact)
      return JsonResponse({'success': True})
    except ObjectDoesNotExist:
      return JsonResponse({'success': False})
  return JsonResponse({'success': False})


@group_required(['training_assistant'])
def assign_trainee_role(request, pk):
  '''Make sure to call assign_destination first'''
  if request.is_ajax() and request.method == "POST":
    field = request.POST.get('field', None)
    if field in DESTINATION_FIELDS:
      trainee_id = request.POST.get('trainee_id', 0)
      is_contact = request.POST.get('is_contact', 'false') == 'true'
      try:
        gt = GospelTrip.objects.get(id=pk)
        tr = Trainee.objects.get(id=trainee_id)
        dests = tr.destination.filter(gospel_trip=gt)
        if dests.exists():
          dest = dests.first()
          dest.set_trainee_as(tr, field, set_to=is_contact)
          dest.save()
          return JsonResponse({'success': True})
        else:
          return JsonResponse({'noDest': True})
      except ObjectDoesNotExist:
        return JsonResponse({'dataError': True})
  return JsonResponse({'badRequest': True})


@csrf_exempt
def upload_image(request):
  form = LocalImageForm(request.POST, request.FILES)
  if form.is_valid():
    f = form.save()
    return JsonResponse({'location': f.file.url}, status=200)
  errors = {f: e.get_json_data() for f, e in form.errors.items()}
  return JsonResponse({'success': 'False', 'errors': errors}, status=500)


@group_required(['training_assistant'])
def clear_application(request, pk, trainee):
  gt = get_object_or_404(GospelTrip, pk=pk)
  tr = get_object_or_404(Trainee, pk=trainee)
  if request.is_ajax() and request.method == "POST":
    Answer.objects.filter(gospel_trip=gt, trainee=tr).update(response=None)
    return JsonResponse({'success': True})
  return JsonResponse({'success': False})
