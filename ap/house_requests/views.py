from itertools import chain

from ap.base_datatable_view import BaseDatatableView  # , DataTableViewerMixin
from aputils.trainee_utils import is_TA
from aputils.utils import modify_model_status
from django.core.serializers import serialize
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from houses.models import Room
from terms.models import Term

from .forms import FramingRequestForm, MaintenanceRequestForm
from .models import FramingRequest, LinensRequest, MaintenanceRequest


class HouseGenericJSON(BaseDatatableView):
  model = None
  fields = ['id', 'trainee_author', 'date_requested', 'house', 'status', ]
  columns = fields
  order_columns = fields
  max_display_length = 120

  def filter_queryset(self, qs):
    search = self.request.GET.get(u'search[value]', None)
    ret = qs.none()
    if search:
      filters = []
      filters.append(Q(trainee_author__firstname__icontains=search))
      filters.append(Q(trainee_author__lastname__icontains=search))
      filters.append(Q(house__name__icontains=search))
      filters.append(Q(id=search))
      for f in filters:
        try:
          ret = ret | qs.filter(f)
        except ValueError:
          continue
      return ret
    else:
      return qs


class MaintenanceRequestJSON(HouseGenericJSON):
  model = MaintenanceRequest


class LinensRequestJSON(HouseGenericJSON):
  model = LinensRequest


class FramingRequestJSON(HouseGenericJSON):
  model = FramingRequest


def NewRequestPage(request):
  return render(request, 'new_request_page.html')


def MaintenanceReport(request):
  if request.POST:
    c = request.POST.get('command')
    key = request.POST.get('pk')
    mr = MaintenanceRequest.objects.filter(pk=key).first()
    if c == "Work Order Created":
      mr.status = 'C'
      mr.save()
    elif c == "Mark for Fellowship":
      mr.status = 'F'
      mr.save()
    elif c == "Delete":
      mr.delete()
    elif c == "Edit":
      mr.TA_comments = request.POST.get('c')
      mr.save()

  data = {}
  data['house_requests'] = MaintenanceRequest.objects.all()
  data['request_status'] = MaintenanceRequest.STATUS

  return render(request, 'maintenance/report.html', context=data)


modify_maintenance_status = modify_model_status(MaintenanceRequest, reverse_lazy('house_requests:maintenance-list'))
modify_linens_status = modify_model_status(LinensRequest, reverse_lazy('house_requests:linens-list'), ['linens'])
modify_framing_status = modify_model_status(FramingRequest, reverse_lazy('house_requests:framing-list'), ['frames'])


class MaintenanceRequestTAComment(generic.UpdateView):
  model = MaintenanceRequest
  fields = ['TA_comments']
  template_name = 'requests/ta_comments.html'


class LinensRequestTAComment(generic.UpdateView):
  model = LinensRequest
  fields = ['TA_comments']
  template_name = 'requests/ta_comments.html'


class FramingRequestTAComment(generic.UpdateView):
  model = FramingRequest
  fields = ['TA_comments']
  template_name = 'requests/ta_comments.html'


class MaintenanceRequestDelete(generic.DeleteView):
  model = MaintenanceRequest
  success_url = reverse_lazy('house_requests:maintenance-list')


class LinensRequestDelete(generic.DeleteView):
  model = LinensRequest
  success_url = reverse_lazy('house_requests:linens-list')


class FramingRequestDelete(generic.DeleteView):
  model = FramingRequest
  success_url = reverse_lazy('house_requests:framing-list')


class RequestCreate(generic.edit.CreateView):
  template_name = 'requests/request_form.html'

  def form_valid(self, form):
    req = form.save(commit=False)
    req.trainee_author = self.request.user
    req.save()
    return super(RequestCreate, self).form_valid(form)


class LinensRequestCreate(RequestCreate, generic.edit.CreateView):
  model = LinensRequest
  success_url = reverse_lazy('house_requests:linens-list')
  fields = ['house', 'request_type', 'quantity', 'request_reason']


class FramingRequestCreate(RequestCreate, generic.edit.CreateView):
  model = FramingRequest
  success_url = reverse_lazy('house_requests:framing-list')
  form_class = FramingRequestForm


class MaintenanceRequestCreate(RequestCreate, generic.edit.CreateView):
  template_name = 'maintenance/request_form.html'
  model = MaintenanceRequest
  success_url = reverse_lazy('house_requests:maintenance-list')
  form_class = MaintenanceRequestForm

  def get_context_data(self, **kwargs):
    ctx = super(MaintenanceRequestCreate, self).get_context_data(**kwargs)
    ctx['rooms'] = serialize('json', Room.objects.all())
    return ctx

  def get_form_kwargs(self):
    kwargs = super(MaintenanceRequestCreate, self).get_form_kwargs()
    kwargs['user'] = self.request.user
    return kwargs


# the following view classes get everything they need from inheritance
class MaintenanceRequestUpdate(MaintenanceRequestCreate, generic.edit.UpdateView):
  pass


class FramingRequestUpdate(FramingRequestCreate, generic.edit.UpdateView):
  pass


class LinensRequestUpdate(LinensRequestCreate, generic.edit.UpdateView):
  pass


class MaintenanceRequestDetail(generic.DetailView):
  model = MaintenanceRequest
  template_name = 'requests/detail_request.html'


class FramingRequestDetail(generic.DetailView):
  model = FramingRequest
  template_name = 'requests/detail_request.html'


class LinensRequestDetail(generic.DetailView):
  model = LinensRequest
  template_name = 'requests/detail_request.html'


class RequestList(generic.ListView):
  template_name = 'request_list/list.html'
  DataTableView = None
  source_url = ''

  def get_queryset(self):
    user_has_service = self.request.user.groups.filter(name__in=['facility_maintenance', 'linens', 'frames']).exists()
    if is_TA(self.request.user) or user_has_service:
      qs = self.model.objects.filter(status='P').filter(date_requested__gte=Term.current_term().get_date(0, 0)) | self.model.objects.filter(status='F').filter(date_requested__gte=Term.current_term().get_date(0, 0))
      return qs.order_by('date_requested')
    else:
      trainee = self.request.user
      return self.model.objects.filter(trainee_author=trainee).filter(date_requested__gte=Term.current_term().get_date(0, 0)).order_by('status')

  def get_context_data(self, **kwargs):
    context = super(RequestList, self).get_context_data(**kwargs)
    user_has_service = self.request.user.groups.filter(name__in=['facility_maintenance', 'linens', 'frames']).exists()
    if is_TA(self.request.user) or user_has_service:
      reqs = self.model.objects.none()
      for status in ['P', 'F', 'C']:
        reqs = chain(reqs, self.model.objects.filter(status=status).filter(date_requested__gte=Term.current_term().get_date(0, 0)).order_by('date_requested'))
      context['reqs'] = reqs
    return context


class MaintenanceRequestList(RequestList):
  model = MaintenanceRequest
  DataTableView = MaintenanceRequestJSON
  modify_status_url = 'house_requests:maintenance-modify-status'
  ta_comment_url = 'house_requests:maintenance-tacomment'
  template_name = 'maintenance/maintenance_list.html'
  source_url = reverse_lazy("house_requests:maintenance-json")


class LinensRequestList(RequestList):
  model = LinensRequest
  DataTableView = LinensRequestJSON
  modify_status_url = 'house_requests:linens-modify-status'
  ta_comment_url = 'house_requests:linens-tacomment'
  source_url = reverse_lazy("house_requests:linens-json")


class FramingRequestList(RequestList):
  model = FramingRequest
  DataTableView = FramingRequestJSON
  modify_status_url = 'house_requests:framing-modify-status'
  ta_comment_url = 'house_requests:framing-tacomment'
  source_url = reverse_lazy("house_requests:framing-json")
