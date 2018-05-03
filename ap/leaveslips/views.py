from itertools import chain
import json

from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect

from rest_framework import filters
from rest_framework_bulk import BulkModelViewSet
from rest_framework.renderers import JSONRenderer
from braces.views import GroupRequiredMixin
from datetime import *

from .models import IndividualSlip, GroupSlip, LeaveSlip
from .forms import IndividualSlipForm, GroupSlipForm
from .serializers import IndividualSlipSerializer, IndividualSlipFilter, GroupSlipSerializer, GroupSlipFilter
from accounts.models import TrainingAssistant, Statistics, Trainee
from attendance.views import react_attendance_context
from aputils.utils import modify_model_status
from aputils.decorators import group_required
from schedules.serializers import AttendanceEventWithDateSerializer


class LeaveSlipUpdate(GroupRequiredMixin, generic.UpdateView):
  def get_context_data(self, **kwargs):
    listJSONRenderer = JSONRenderer()
    ctx = super(LeaveSlipUpdate, self).get_context_data(**kwargs)
    trainee = self.get_object().get_trainee_requester()
    ctx.update(react_attendance_context(trainee))
    ctx['Today'] = self.get_object().get_date().strftime('%m/%d/%Y')
    ctx['SelectedEvents'] = listJSONRenderer.render(AttendanceEventWithDateSerializer(self.get_object().events, many=True).data)
    ctx['default_transfer_ta'] = self.request.user.TA or self.get_object().TA
    return ctx


class IndividualSlipUpdate(LeaveSlipUpdate):
  model = IndividualSlip
  group_required = ['training_assistant']
  template_name = 'leaveslips/individual_update.html'
  form_class = IndividualSlipForm
  context_object_name = 'leaveslip'

  def get_context_data(self, **kwargs):
    ctx = super(IndividualSlipUpdate, self).get_context_data(**kwargs)
    if self.get_object().type in ['MEAL', 'NIGHT']:
      IS_list = IndividualSlip.objects.filter(status='A', trainee=self.get_object().get_trainee_requester(), type=self.get_object().type).order_by('-submitted')
      most_recent_IS = IS_list.first()
      if most_recent_IS and most_recent_IS != self.get_object():
        last_date = most_recent_IS.rolls.all().order_by('date').last().date
        ctx['last_date'] = last_date
        ctx['days_since'] = (self.get_object().rolls.first().date - last_date).days
    ctx['show'] = 'leaveslip'
    return ctx

  def post(self, request, **kwargs):
    events = json.loads(request.POST.get('events', '[]'))
    if events:
      IndividualSlipSerializer().update(self.get_object(), {'events': events})
    return super(IndividualSlipUpdate, self).post(request, **kwargs)


class GroupSlipUpdate(LeaveSlipUpdate):
  model = GroupSlip
  group_required = ['training_assistant']
  template_name = 'leaveslips/group_update.html'
  form_class = GroupSlipForm
  context_object_name = 'leaveslip'


# viewing the leave slips
class LeaveSlipList(generic.ListView):
  model = IndividualSlip, GroupSlip
  template_name = 'leaveslips/list.html'

  def get_queryset(self):
   individual = IndividualSlip.objects.filter(trainee=self.request.user.id).order_by('status')
   group = GroupSlip.objects.filter(trainee=self.request.user.id).order_by('status')  # if trainee is in a group leaveslip submitted by another user
   queryset = chain(individual, group, )  # combines two querysets
   return queryset


class TALeaveSlipList(GroupRequiredMixin, generic.TemplateView):
  model = IndividualSlip, GroupSlip
  group_required = ['training_assistant']
  template_name = 'leaveslips/ta_list.html'

  def post(self, request, *args, **kwargs):
    context = self.get_context_data()
    return super(TALeaveSlipList, self).render_to_response(context)

  def get_context_data(self, **kwargs):
    ctx = super(TALeaveSlipList, self).get_context_data(**kwargs)

    individual = IndividualSlip.objects.all().order_by('status', 'submitted')
    group = GroupSlip.objects.all().order_by('status', 'submitted')  # if trainee is in a group leave slip submitted by another user

    s, _ = Statistics.objects.get_or_create(trainee=self.request.user)

    slip_setting = s.settings.get('leaveslip')
    selected_ta = slip_setting.get('selected_ta', self.request.user.id)
    status = slip_setting.get('selected_status', 'P')
    selected_trainee = slip_setting.get('selected_trainee', Trainee.objects.first().id)

    if self.request.method == 'POST':
      selected_ta = int(self.request.POST.get('leaveslip_ta_list'))
      status = self.request.POST.get('leaveslip_status')
      selected_trainee = self.request.POST.get('leaveslip_trainee_list')
    else:
      status = self.request.GET.get('status', status)
      selected_ta = self.request.GET.get('ta', selected_ta)
      selected_trainee = self.request.GET.get('trainee')

    s.settings['leaveslip']['selected_ta'] = selected_ta
    s.settings['leaveslip']['selected_status'] = status
    s.settings['leaveslip']['selected_trainee'] = selected_trainee
    s.save()

    ta = None
    if int(selected_ta) > 0:
      ta = TrainingAssistant.objects.filter(pk=selected_ta).first()
      individual = individual.filter(TA=ta)
      group = group.filter(TA=ta)

    tr = None  # selected_trainee
    if selected_trainee and int(selected_trainee) > 0:
      tr = Trainee.objects.filter(pk=selected_trainee).first()
      individual = individual.filter(trainee=tr)
      group = group.filter(trainees__in=[tr])


    if status != "-1":
      si_slips = IndividualSlip.objects.none()
      sg_slips = GroupSlip.objects.none()
      if status == 'P':
        si_slips = individual.filter(status='S')
        sg_slips = group.filter(status='S')
      individual = individual.filter(status=status) | si_slips
      group = group.filter(status=status) | sg_slips

    # Prefetch for performance
    individual.select_related('trainee', 'TA', 'TA_informed').prefetch_related('rolls')
    group.select_related('trainee', 'TA', 'TA_informed').prefetch_related('trainees')

    ctx['TA_list'] = TrainingAssistant.objects.filter(groups__name='regular_training_assistant')
    ctx['leaveslips'] = chain(individual, group)  # combines two querysets
    ctx['selected_ta'] = ta
    ctx['status_list'] = LeaveSlip.LS_STATUS[:-1]  # Removes Sister Approved Choice
    ctx['selected_status'] = status
    ctx['selected_trainee'] = tr
    ctx['trainee_list'] = Trainee.objects.all()
    return ctx


@group_required(('training_assistant',), raise_exception=True)
def modify_status(request, classname, status, id):
  model = IndividualSlip
  if classname == "group":
    model = GroupSlip
  list_link = modify_model_status(model, reverse_lazy('leaveslips:ta-leaveslip-list'))(request, status,
                id, lambda obj: "%s's %s was %s" % (obj.requester_name, obj._meta.verbose_name, obj.get_status_for_message()))
  if "update" in request.META.get('HTTP_REFERER'):
    next_ls = IndividualSlip.objects.filter(status__in=['P', 'S'], TA=request.user).first()
    if next_ls:
      return redirect(reverse_lazy('leaveslips:individual-update', kwargs={'pk': next_ls.pk}))
    next_ls = GroupSlip.objects.filter(status__in=['P', 'S'], TA=request.user).first()
    if next_ls:
      return redirect(reverse_lazy('leaveslips:group-update', kwargs={'pk': next_ls.pk}))
  return list_link


@group_required(('training_assistant',), raise_exception=True)
def bulk_modify_status(request, status):
  individual = []
  group = []
  for key, value in request.POST.iteritems():
    if value == "individual":
      individual.append(key)
    else:
      group.append(key)
  if individual:
    IndividualSlip.objects.filter(pk__in=individual).update(status=status)
  if group:
    GroupSlip.objects.filter(pk__in=group).update(status=status)
  sample = IndividualSlip.objects.get(pk=individual[0]) if individual else GroupSlip.objects.get(pk=group[0])
  message = "%s %ss were %s" % (len(individual) + len(group), LeaveSlip._meta.verbose_name, sample.get_status_for_message())
  messages.add_message(request, messages.SUCCESS, message)
  return redirect(reverse_lazy('leaveslips:ta-leaveslip-list'))


# API Views
class IndividualSlipViewSet(BulkModelViewSet):
  queryset = IndividualSlip.objects.all()
  serializer_class = IndividualSlipSerializer
  filter_backends = (filters.DjangoFilterBackend, )
  filter_class = IndividualSlipFilter

  def get_queryset(self):
    user = self.request.user
    if not user.groups.filter(name='attendance_monitors').exists():
      individualslip = IndividualSlip.objects.filter(trainee=user)
    else:
      individualslip = IndividualSlip.objects.all()
    return individualslip

  def allow_bulk_destroy(self, qs, filtered):
    return filtered


class GroupSlipViewSet(BulkModelViewSet):
  queryset = GroupSlip.objects.all()
  serializer_class = GroupSlipSerializer
  filter_backends = (filters.DjangoFilterBackend,)
  filter_class = GroupSlipFilter

  def get_queryset(self):
    user = self.request.user
    if not user.groups.filter(name='attendance_monitors').exists():
      groupslip = GroupSlip.objects.filter(Q(trainees=user) | Q(trainee=user)).distinct()
    else:
      groupslip = GroupSlip.objects.all()
    return groupslip

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class AllIndividualSlipViewSet(BulkModelViewSet):
  queryset = IndividualSlip.objects.all()
  serializer_class = IndividualSlipSerializer
  filter_backends = (filters.DjangoFilterBackend, )
  filter_class = IndividualSlipFilter

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class AllGroupSlipViewSet(BulkModelViewSet):
  queryset = GroupSlip.objects.all()
  serializer_class = GroupSlipSerializer
  filter_backends = (filters.DjangoFilterBackend,)
  filter_class = GroupSlipFilter

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)
