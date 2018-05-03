from datetime import datetime

from django.views.generic.edit import UpdateView
from django.views.generic import *

from .models import *
from .forms import XBApplicationForm
from terms.models import Term


class XBApplicationView(UpdateView):
  model = XBApplication
  form_class = XBApplicationForm
  template_name = 'xb_application/application_form.html'

  def get_object(self):
    admin, created = XBAdmin.objects.get_or_create(term=Term.current_term())
    xbApp, created = XBApplication.objects.get_or_create(trainee=self.request.user, xb_admin=admin)
    return xbApp

  def post(self, request, *args, **kwargs):
    self.object = self.get_object()
    return super(XBApplicationView, self).post(request, *args, **kwargs)

  def form_valid(self, form):
    xbApp = form.save(commit=False)
    xbApp.xb_admin = XBAdmin.objects.get_or_create(term=Term.current_term())[0]
    xbApp.trainee = self.request.user

    if 'submit' in self.request.POST:
      xbApp.submitted = True
      xbApp.date_submitted = datetime.now()
    xbApp.last_updated = datetime.now()
    xbApp.save()

    return super(XBApplicationView, self).form_valid(form)

  def get_context_data(self, **kwargs):
    ctx = super(XBApplicationView, self).get_context_data(**kwargs)
    self.object = self.get_object()
    ctx['submitted'] = self.object.submitted
    ctx['last_updated'] = self.object.last_updated
    ctx['page_title'] = 'FTTA-XB Application'
    ctx['term'] = Term.next_term()
    if self.object.xb_admin.xb_due_date:
      ctx['due_date'] = self.object.xb_admin.xb_due_date
    today = datetime.now().date()
    if self.object.xb_admin.xb_show_status == 'SHOW' or today > self.object.xb_admin.xb_due_date:
      ctx['read_only'] = True
    if not self.object.submitted:
      ctx['save_button'] = '<button type="submit" class="btn btn-primary btn-save">Save</button>'
      ctx['submit_button'] = '<button type="submit" class="btn btn-primary btn-save" name="submit">Submit</button>'
    return ctx


class XBReportView(ListView):
  model = XBApplication
  template_name = 'xb_application/xb_report.html'

  def get_queryset(self):
    return self.model.objects.all()

  def get_context_data(self, **kwargs):
    ctx = super(XBReportView, self).get_context_data(**kwargs)
    ctx['trainees'] = self.model.objects.filter(trainee__current_term=4, last_updated__isnull=False)
    ctx['page_title'] = 'FTTA-XB Application Report List'
    return ctx


class XBApplicationDetails(DetailView):
  model = XBApplication
  template_name = 'xb_application/xb_detail.html'

  def get_context_data(self, **kwargs):
    ctx = super(XBApplicationDetails, self).get_context_data(**kwargs)
    obj = self.get_object()
    ctx['object'] = self.model.objects.filter(pk=obj.id).values()[0]
    ctx['trainee'] = obj.trainee
    ctx['term'] = obj.xb_admin.term.next_term
    ctx['narrative_wc'] = 0
    if obj.narrative is not None and obj.narrative != "":
      ctx['narrative_wc'] = len(obj.narrative.split(" "))
    return ctx
