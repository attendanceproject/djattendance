# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.edit import UpdateView
from django.views.generic import ListView
from django.template.defaultfilters import title
from django.shortcuts import redirect

from terms.models import Term
from graduation.models import *
from graduation.forms import *
from xb_application.forms import XBAdminForm
from xb_application.models import XBAdmin

from braces.views import GroupRequiredMixin

from datetime import datetime
from collections import OrderedDict

MODELS = [Testimony, Consideration, Website, Outline, Remembrance, Misc]


class CreateUpdateView(UpdateView):
  template_name = 'graduation/graduation_form.html'

  def get_object(self, queryset=None):
    grad_admin, created = GradAdmin.objects.get_or_create(term=Term.current_term())
    obj, created = self.model.objects.get_or_create(trainee=self.request.user, grad_admin=grad_admin)
    return obj

  def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    return super(CreateUpdateView, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    self.object = self.get_object()
    return super(CreateUpdateView, self).post(request, *args, **kwargs)

  def form_valid(self, form):
    return super(CreateUpdateView, self).form_valid(form)

  def get_context_data(self, **kwargs):
    ctx = super(CreateUpdateView, self).get_context_data(**kwargs)
    today = datetime.now().date()
    if self.object.show_status == 'SHOW' or today > self.object.due_date:
      ctx['read_only'] = True
    ctx['page_title'] = self.object.name_of_model
    ctx['button_label'] = 'Save'
    return ctx


class TestimonyView(CreateUpdateView):
  model = Testimony
  form_class = TestimonyForm
  template_name = 'graduation/testimony.html'


class ConsiderationView(CreateUpdateView):
  model = Consideration
  form_class = ConsiderationForm
  template_name = 'graduation/consideration.html'


class WebsiteView(CreateUpdateView):
  model = Website
  form_class = WebsiteForm


class OutlineView(CreateUpdateView):
  model = Outline
  form_class = OutlineForm
  template_name = 'graduation/outline.html'

  # hack for those speaking, needs to be cleaned up and used the proper methods, override the default clean methods
  # instead of using a form invalid as a hack
  def form_invalid(self, form):
    obj = self.object
    obj.speaking_section = form.cleaned_data['speaking_section']
    obj.speaking = form.cleaned_data['speaking']
    obj.save()
    return redirect('graduation:outline-view')

class RemembranceView(CreateUpdateView):
  model = Remembrance
  form_class = RemembranceForm
  template_name = 'graduation/remembrance.html'


class MiscView(CreateUpdateView):
  model = Misc
  form_class = MiscForm
  template_name = 'graduation/misc.html'

  def get_context_data(self, **kwargs):
    ctx = super(MiscView, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Grad Invites & DVDs'

    return ctx


class GradAdminView(GroupRequiredMixin, UpdateView):
  model = GradAdmin
  form_class = GradAdminForm
  template_name = 'graduation/grad_admin.html'
  group_required = ['training_assistant', 'grad_committee']

  def get_object(self, queryset=None):
    obj, created = self.model.objects.get_or_create(term=Term.current_term())
    return obj

  def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    return super(GradAdminView, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    self.object = self.get_object()

    if all(x in request.POST for x in ['xb_show_status', 'xb_due_date']):
      self.xb_form_valid(request.POST)

    return super(GradAdminView, self).post(request, *args, **kwargs)

  def xb_form_valid(self, data):
    term = Term.current_term()
    print term
    xb, created = XBAdmin.objects.get_or_create(term=term)
    print xb
    form = XBAdminForm(data, instance=xb)
    print form
    form.save()

  def form_valid(self, form):
    return super(GradAdminView, self).form_valid(form)

  def get_statistics(self):
    term = Term.current_term()
    return OrderedDict([(m.__name__ + ' responses', m.responded_number(term)) for m in MODELS])

  def get_context_data(self, **kwargs):
    ctx = super(GradAdminView, self).get_context_data(**kwargs)
    ctx['stats'] = self.get_statistics()
    ctx['page_title'] = "Grad Admin"
    ctx['button_label'] = 'Save'
    ctx['4th_count'] = Misc.objects.filter(grad_admin=GradAdmin.objects.get(term=Term.objects.filter(current=True).first()), trainee__in=Trainee.objects.filter(current_term=4)).count()
    # xb form
    term = Term.current_term()
    xba = XBAdmin.objects.filter(term=term)
    if xba:
      ctx['xb_form'] = XBAdminForm(instance=xba.first())
    else:
      ctx['xb_form'] = XBAdminForm()
    return ctx


class ReportView(GroupRequiredMixin, ListView):
  group_required = ['training_assistant', 'grad_committee']

  def get_context_data(self, **kwargs):
    context = super(ReportView, self).get_context_data(**kwargs)
    context['data'] = self.model.objects.filter(trainee__current_term=4)
    context['title'] = title(self.model._meta.verbose_name + ' Report')

    return context


class TestimonyReport(ReportView):
  model = Testimony
  template_name = 'graduation/testimony_report.html'


class ConsiderationReport(ReportView):
  model = Consideration
  template_name = 'graduation/consideration_report.html'


class WebsiteReport(ReportView):
  model = Website
  template_name = 'graduation/website_report.html'


class OutlineReport(ReportView):
  model = Outline
  template_name = 'graduation/outline_report.html'


class SpeakingReport(ReportView):
  model = Outline
  template_name = 'graduation/speaking_report.html'

  def get_context_data(self, **kwargs):
    context = super(SpeakingReport, self).get_context_data(**kwargs)
    speaking_trainees = GradAdmin.objects.get(term=Term.current_term()).speaking_trainees.all()
    context['data'] = Outline.objects.filter(trainee__in=speaking_trainees)
    context['title'] = 'Speaking Report'

    return context


class MiscReport(ReportView):
  model = Misc
  template_name = 'graduation/misc_report.html'

  def get_context_data(self, **kwargs):
    context = super(MiscReport, self).get_context_data(**kwargs)
    context['dvd_totals'] = sum(filter(None, (o.grad_dvd for o in context['data'])))
    context['invite_totals'] = sum(filter(None, (o.grad_invitations for o in context['data'])))

    return context


class RemembranceReport(ReportView):
  model = Remembrance
  template_name = 'graduation/rem_report.html'
