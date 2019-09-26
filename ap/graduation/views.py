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
term = Term.current_term()


class CreateUpdateView(UpdateView):
  template_name = 'graduation/graduation_form.html'

  def get_object(self, queryset=None):
    grad_admin, created = GradAdmin.objects.get_or_create(term=term)
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
    ctx['read_only'] = (self.object.show_status == 'SHOW')
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
    obj.speaking_section = form.cleaned_data.get('speaking_section')
    obj.speaking = form.cleaned_data.get('speaking')
    obj.save()
    return redirect('graduation:outline-view')

class RemembranceView(CreateUpdateView):
  model = Remembrance
  form_class = RemembranceForm
  template_name = 'graduation/remembrance.html'

  def get_context_data(self, **kwargs):
    ctx = super(RemembranceView, self).get_context_data(**kwargs)
    ctx['rem_limit'] = self.object.grad_admin.remembrance_char_limit

    return ctx


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
    obj, created = self.model.objects.get_or_create(term=term)
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
    xb, created = XBAdmin.objects.get_or_create(term=term)
    form = XBAdminForm(data, instance=xb)
    form.save()

  def form_valid(self, form):
    return super(GradAdminView, self).form_valid(form)

  def get_statistics(self):
    return OrderedDict([(m.__name__ + ' responses', m.responded_number(term)) for m in MODELS])

  def get_context_data(self, **kwargs):
    ctx = super(GradAdminView, self).get_context_data(**kwargs)
    ctx['stats'] = self.get_statistics()
    ctx['page_title'] = "Grad Admin"
    ctx['button_label'] = 'Save'
    ctx['4th_count'] = Misc.objects.filter(grad_admin=GradAdmin.objects.get(term=Term.objects.filter(current=True).first()), trainee__in=Trainee.objects.filter(current_term=4)).count()
    # speaking
    speaking_trainees = GradAdmin.objects.get(term=term).speaking_trainees.all()
    oset = Outline.objects.filter(grad_admin__term=term, trainee__in=speaking_trainees)
    ctx['speaking_stat'] = {
      'count': speaking_trainees.count(),
      'responses': len(filter(lambda o: o.speaking or o.speaking, oset))
    }
    # xb form
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
    context['data'] = self.model.objects.filter(grad_admin__term=term, trainee__current_term=4)
    not_completed = filter(lambda o: not o.responded, context['data'])
    nc = [(x.trainee.firstname + " " + x.trainee.lastname) for x in not_completed]
    context['not_completed_trainees'] = sorted(nc)
    context['not_completed_number'] = len(nc)
    context['title'] = title(self.model._meta.verbose_name + ' Report')

    return context


class TestimonyReport(ReportView):
  model = Testimony
  template_name = 'graduation/testimony_report.html'


class ConsiderationReport(ReportView):
  model = Consideration
  template_name = 'graduation/consideration_report.html'

  def get_context_data(self, **kwargs):
    context = super(ConsiderationReport, self).get_context_data(**kwargs)

    xb_choices = ['YES', 'OPEN', 'NO', 'OTHER', None]
    xb_count = [0, 0, 0, 0, 0]
    fellowshipped_choices = ['YES', 'NO', 'OTHER', None]
    fellowshipped_count = [0, 0, 0, 0]

    for c in context['data']:
      xb_count[xb_choices.index(c.attend_XB)] += 1
      fellowshipped_count[fellowshipped_choices.index(c.fellowshipped)] += 1

    fourth_termers_count = len(context['data'])
    xb_percent = [100 * x / float(fourth_termers_count) for x in xb_count]
    fellowshipped_percent = [100 * x / float(fourth_termers_count) for x in fellowshipped_count]

    context['xb_display'] = "Attend Boston?\tYes: %0.2f%% (%d/%d)\tOpen: %0.2f%% (%d/%d)\tNo: %0.2f%% (%d/%d)\tOther: %0.2f%% (%d/%d)\tNo Response: %0.2f%% (%d/%d)" % (xb_percent[0], xb_count[0], fourth_termers_count, xb_percent[1], xb_count[1], fourth_termers_count, xb_percent[2], xb_count[2], fourth_termers_count, xb_percent[3], xb_count[3], fourth_termers_count, xb_percent[4], xb_count[4], fourth_termers_count)
    context['fellowshipped_display'] = "Fellowshipped?\tYes: %0.2f%% (%d/%d)\t\t\t\tNo: %0.2f%% (%d/%d)\tScheduled: %0.2f%% (%d/%d)\tNo Response: %0.2f%% (%d/%d)" % (fellowshipped_percent[0], fellowshipped_count[0], fourth_termers_count, fellowshipped_percent[1], fellowshipped_count[1], fourth_termers_count, fellowshipped_percent[2], fellowshipped_count[2], fourth_termers_count, fellowshipped_percent[3], fellowshipped_count[3], fourth_termers_count,)

    return context


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
    speaking_trainees = GradAdmin.objects.get(term=term).speaking_trainees.all()
    context['data'] = Outline.objects.filter(grad_admin__term=term, trainee__in=speaking_trainees)
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
