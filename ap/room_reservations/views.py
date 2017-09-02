from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q

from .models import RoomReservation
from .forms import RoomReservationForm
from accounts.models import Trainee
from rooms.models import Room
from aputils.groups_required_decorator import group_required

import json
from datetime import datetime, timedelta, time
from braces.views import GroupRequiredMixin

class RoomReservationSubmit(CreateView):
  model = RoomReservation
  template_name = 'room_reservations/room_reservation.html'
  form_class = RoomReservationForm

  def get_context_data(self, **kwargs):
    ctx = super(RoomReservationSubmit, self).get_context_data(**kwargs)
    
    all_reservations = RoomReservation.objects.all().order_by('-submitted')
    approved_reservations = RoomReservation.objects.filter(Q(status='A'))
    rooms = Room.objects.all()
    approved_reservations_json = serialize('json', approved_reservations)
    rooms_json = serialize('json', rooms)
    times = ['%s:%s%s' % (h, m, ap) for ap in ('am', 'pm') \
      for h in ([12] + list(range(1,12))) \
      for m in ('00', '30')]
    bro_rooms = Room.objects.filter(Q(access='B'))
    sis_rooms = Room.objects.filter(Q(access='S'))

    ctx['all_reservations'] = all_reservations
    ctx['approved_reservations'] = approved_reservations_json
    ctx['rooms_list'] = rooms_json
    ctx['bro_rooms_list'] = serialize('json', bro_rooms)
    ctx['sis_rooms_list'] = serialize('json', sis_rooms)
    ctx['times_list'] = times
    ctx['page_title'] = 'Submit New Request'
    ctx['button_label'] = 'Submit'
    return ctx

  def form_valid(self, form):
    room_reservation = form.save(commit=False)
    room_reservation.trainee = Trainee.objects.get(id=self.request.user.id)
    room_reservation.save()
    return HttpResponseRedirect(reverse('room_reservations:room-reservation-submit'))

class RoomReservationUpdate(UpdateView):
  model = RoomReservation
  template_name = 'room_reservations/room_reservation.html'
  form_class = RoomReservationForm
  context_object_name = 'room_reservation'

  def get_context_data(self, **kwargs):
    ctx = super(RoomReservationUpdate, self).get_context_data(**kwargs)
    room_reservation = self.get_object()
    reservations = RoomReservation.objects.exclude(id=room_reservation.id).filter(Q(status='P')|Q(status='F'))
    ctx['reservations'] = reservations
    ctx['page_title'] = 'Edit Request'
    ctx['button_label'] = 'Update'
    return ctx

  def form_valid(self, form):
    room_reservation = form.save(commit=False)
    room_reservation.save()
    return HttpResponseRedirect(reverse('room_reservations:room-reservation-submit'))

class TARoomReservationList(GroupRequiredMixin, TemplateView):
  model = RoomReservation
  group_required = ['administration']
  template_name = 'room_reservations/ta_list.html'

  def get_context_data(self, **kwargs):
    ctx = super(TARoomReservationList, self).get_context_data(**kwargs)
    reservations = RoomReservation.objects.filter(Q(status='P')|Q(status='F'))
    ctx['reservations'] = reservations
    return ctx

class RoomReservationSchedule(GroupRequiredMixin, TemplateView):
  model = RoomReservation
  group_required = ['administration']
  template_name = 'room_reservations/schedule.html'

  def get_context_data(self, **kwargs):
    ctx = super(RoomReservationSchedule, self).get_context_data(**kwargs)
    reservations = RoomReservation.objects.filter(Q(status='A'))
    rooms = Room.objects.all()
    reservations_json = serialize('json', reservations)
    rooms_json = serialize('json', rooms)
    times = ['%s:%s%s' % (h, m, ap) for ap in ('am', 'pm') \
      for h in ([12] + list(range(1,12))) \
      for m in ('00', '30')]
    bro_rooms = Room.objects.filter(Q(access='B'))
    sis_rooms = Room.objects.filter(Q(access='S'))

    # generate time range
    ctx['reservations'] = reservations_json
    ctx['rooms_list'] = rooms_json
    ctx['bro_rooms_list'] = serialize('json', bro_rooms)
    ctx['sis_rooms_list'] = serialize('json', sis_rooms)
    ctx['times_list'] = times
    return ctx

@group_required(('administration',), raise_exception=True)
def reservation_modify_status(request, status, id):
  reservation = get_object_or_404(RoomReservation, pk=id)
  reservation.status = status
  reservation.save()

  message = "%s's room reservation was " %(reservation.trainee)
  if status == 'A':
    message += 'approved.'
  if status == 'D':
    message += 'denied.'
  if status == 'F':
    message += 'marked for fellowship.'

  messages.add_message(request, messages.SUCCESS, message)
  return redirect(reverse('room_reservations:ta-room-reservation-list'))
