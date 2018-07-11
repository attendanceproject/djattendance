# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from accounts.models import Trainee
from aputils.trainee_utils import is_trainee, trainee_from_user
from braces.views import GroupRequiredMixin
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic import UpdateView
from semi.forms import AttendanceForm, LocationForm
from semi.models import SemiAnnual
from semi.utils import attendance_stats, ROLL_STATUS
from terms.models import Term


class LocationUpdate(UpdateView):
  model = SemiAnnual
  form_class = LocationForm
  template_name = 'semi/location_form.html'

  def dispatch(self, request, *args, **kwargs):
    if request.method == 'GET' and not self.kwargs.get('pk', None):
      term = Term.current_term()
      if is_trainee(request.user):
        trainee = trainee_from_user(request.user)
      else:
        trainee = Trainee.objects.first()
      semi = SemiAnnual.objects.get_or_create(trainee=trainee, term=term)[0]
      return redirect(reverse('semi:location', kwargs={'pk': semi.pk}))
    return super(LocationUpdate, self).dispatch(request, *args, **kwargs)

  def get_success_url(self):
    return self.object.get_location_url()

  def get_context_data(self, **kwargs):
    context = super(LocationUpdate, self).get_context_data(**kwargs)
    context['term'] = self.object.term
    context['page_title'] = "Study Location Form"
    context['button_label'] = "Save"
    return context


class AttendanceUpdate(TemplateView):
  template_name = 'semi/attendance_form.html'
  semi = None

  def dispatch(self, request, *args, **kwargs):
    if request.method == 'GET' and not self.kwargs.get('pk', None):
      term = Term.current_term()
      if is_trainee(request.user):
        trainee = trainee_from_user(request.user)
      else:
        trainee = Trainee.objects.first()
      semi = SemiAnnual.objects.get_or_create(trainee=trainee, term=term)[0]
      return redirect(reverse('semi:attendance', kwargs={'pk': semi.pk}))
    return super(AttendanceUpdate, self).dispatch(request, *args, **kwargs)

  def get(self, request, *args, **kwargs):
    self.semi = get_object_or_404(SemiAnnual, pk=self.kwargs['pk'])
    return super(AttendanceUpdate, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    self.semi = get_object_or_404(SemiAnnual, pk=self.kwargs['pk'])
    form = AttendanceForm(request.POST)
    if form.is_valid():
      data = form.cleaned_data
      self.semi.location = data.pop('location')
      for k, v in data.items():
        if v:
          self.semi.attendance[k] = v
      self.semi.save()
    context = self.get_context_data()
    return super(AttendanceUpdate, self).render_to_response(context)

  def get_context_data(self, **kwargs):
    context = super(AttendanceUpdate, self).get_context_data(**kwargs)
    init = self.semi.attendance
    init.update({'location': self.semi.location})
    headers = [rs[1] for rs in ROLL_STATUS]
    headers.insert(0, '')
    context['headers'] = headers
    context['form'] = AttendanceForm(initial=init)
    context['term'] = self.semi.term
    context['page_title'] = "Personal Study Attendance Form"
    context['button_label'] = "Save"
    return context


class AttendanceReport(GroupRequiredMixin, TemplateView):
  template_name = 'semi/attendance_report.html'
  group_required = ['training_assistant']

  @staticmethod
  def get_report_context():
    term = Term.current_term()
    semis = SemiAnnual.objects.filter(term=term)
    data = []
    for t in Trainee.objects.all():
      d = {'name': t.full_name, 'term': t.current_term}
      if semis.filter(trainee=t).exists():
        semi = semis.get(trainee=t)
        if 'N' in semi.attendance.values():
          d['submitted'] = "No"
        else:
          d['submitted'] = "Yes"
          d['semi'] = semi
          d['stats'] = attendance_stats(semi)
      else:
        d['submitted'] = "No"
      data.append(d)
    return data

  def get_context_data(self, **kwargs):
    context = super(AttendanceReport, self).get_context_data(**kwargs)
    context['page_title'] = "Attendance Report"
    context['term'] = Term.current_term()
    context['data'] = self.get_report_context()
    return context


class LocationReport(GroupRequiredMixin, TemplateView):
  template_name = 'semi/location_report.html'
  group_required = ['training_assistant']

  @staticmethod
  def get_report_context():
    term = Term.current_term()
    semis = SemiAnnual.objects.filter(term=term)
    data = []
    for t in Trainee.objects.all():
      d = {'name': t.full_name, 'term': t.current_term, 'gender': t.gender}
      if semis.filter(trainee=t).exists():
        semi = semis.get(trainee=t)
        d['semi'] = semi
      data.append(d)
    return data

  def get_context_data(self, **kwargs):
    context = super(LocationReport, self).get_context_data(**kwargs)
    context['page_title'] = "Location Report"
    context['term'] = Term.current_term()
    context['data'] = self.get_report_context()
    return context
