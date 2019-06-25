from itertools import chain

from ap.base_datatable_view import BaseDatatableView  # , DataTableViewerMixin
from aputils.decorators import group_required
from aputils.trainee_utils import is_TA, trainee_from_user
from aputils.utils import modify_model_status
from django.contrib import messages
# from django.db import models
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic
from terms.models import Term

from . import utils
from .forms import (DirectWebAccess, EShepherdingRequest,
                    WebAccessRequestCreateForm,
                    WebAccessRequestGuestCreateForm,
                    WebAccessRequestTACommentForm)
from .models import WebRequest


class WebRequestJSON(BaseDatatableView):
  model = WebRequest
  columns = ['id', 'trainee', 'reason', 'minutes', 'date_assigned', 'status', ]
  order_columns = ['id', 'trainee', '', '', 'date_assigned', 'status', ]
  max_display_length = 120

  def filter_queryset(self, qs):
    search = self.request.GET.get(u'search[value]', None)
    ret = qs.none()
    if search:
      filters = []
      filters.append(Q(trainee__firstname__icontains=search))
      filters.append(Q(trainee__lastname__icontains=search))
      filters.append(Q(id=search))
      for f in filters:
        try:
          ret = ret | qs.filter(f)
        except ValueError:
          continue
      return ret
    else:
      return qs


class WebAccessMixin(object):
  model = WebRequest
  template_name = 'requests/request_form.html'
  form_class = WebAccessRequestCreateForm
  success_url = reverse_lazy('web_access:web_access-list')


class WebAccessCreate(WebAccessMixin, generic.CreateView):
  def form_valid(self, form):
    req = form.save(commit=False)
    req.trainee = trainee_from_user(self.request.user)
    req.save()
    message = "Created new web request."
    messages.add_message(self.request, messages.SUCCESS, message)
    return super(WebAccessCreate, self).form_valid(form)


class WebAccessUpdate(WebAccessMixin, generic.UpdateView):
  pass


class WebAccessDelete(WebAccessMixin, generic.DeleteView):
  model = WebRequest
  success_url = reverse_lazy('web_access:web_access-list')



class WebAccessDetail(generic.DetailView):
  model = WebRequest
  template_name = 'requests/detail_request.html'


class WebRequestList(generic.ListView):
  model = WebRequest
  template_name = 'web_access/web_access_list.html'
  DataTableView = WebRequestJSON
  source_url = reverse_lazy("web_access:web_access-json")

  def get_queryset(self):
    if is_TA(self.request.user):
      qs = WebRequest.objects.filter(status='P') | WebRequest.objects.filter(status='F')
      return qs.order_by('date_assigned')
    else:
      trainee = trainee_from_user(self.request.user)
      qset = WebRequest.objects.filter(trainee=trainee).order_by('status')
    return qset

  def get_context_data(self, **kwargs):
    context = super(WebRequestList, self).get_context_data(**kwargs)
    if is_TA(self.request.user):
      wars = WebRequest.objects.none()
      for status in ['P', 'F', 'A', 'D']:
        wars = chain(wars, WebRequest.objects.filter(status=status).filter(date_assigned__gte=Term.current_term().get_date(0, 0)).order_by('date_assigned'))
      context['wars'] = wars
    # if not is_TA(self.request.user):
    #   del context['source_url']
    #   del context['header']
    #   del context['targets_list']
    return context


class TAWebAccessUpdate(WebAccessMixin, generic.UpdateView):
  template_name = 'requests/ta_comments.html'
  form_class = WebAccessRequestTACommentForm
  raise_exception = True


modify_status = modify_model_status(WebRequest, reverse_lazy('web_access:web_access-list'))


def getGuestRequests(request):
  """ Returns list of requests identified by MAC address """
  mac = utils._getMAC(utils._getIPAddress(request))
  requests = WebRequest.objects.all().filter(trainee=None, mac_address=mac).order_by('status')
  print(mac)
  html = render(request, 'web_access/requests_panel.html', context={'guest_access_requests': requests})
  return HttpResponse(html)


def eShepherdingRequest(request):
  if request.method == 'POST':
    form = EShepherdingRequest(request.POST)
    if form.is_valid():
      mac = utils._getMAC(utils._getIPAddress(request))
      if mac is not None:
        utils.startAccessFromMacAddress(request, '30', mac)
      else:
        message = "Mac address location failed."
        messages.add_message(request, messages.ERROR, message)
      return redirect('web_access:eshepherding-access')
  else:
    form = EShepherdingRequest()
  return render(request, 'web_access/eshepherding_access.html', {'form': form})


def createGuestWebAccess(request):
  if request.method == 'POST':
    mac = utils._getMAC(utils._getIPAddress(request))
    form = WebAccessRequestGuestCreateForm(request.POST)
    if form.is_valid():
      instance = form.save(commit=False)
      instance.mac_address = mac
      instance.save()
    return HttpResponse('Submitted!')
  else:
    return HttpResponse('Error: This is a private endpoint, only accept post')


def deleteGuestWebAccess(request, id):
  WebRequest.objects.filter(id=id).delete()
  return getGuestRequests(request)


@group_required(('training_assistant', 'networks'), raise_exception=True)
def directWebAccess(request):
  if request.method == 'POST':
    form = DirectWebAccess(request.POST)
    if form.is_valid():
      utils.startAccessFromMacAddress(
          request,
          form.cleaned_data.get('minutes'),
          form.cleaned_data.get('mac_address')
      )
      return redirect('web_access:direct-web-access')
  else:
    form = DirectWebAccess()

  return render(request, 'web_access/direct_web_access.html', {'form': form})
