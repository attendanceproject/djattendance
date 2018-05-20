import requests
import json
from datetime import date

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponse

from .models import RoomReservation
from .forms import RoomReservationForm
from accounts.models import TrainingAssistant, User
from rooms.models import Room
from aputils.trainee_utils import is_TA
from aputils.utils import modify_model_status

from braces.views import GroupRequiredMixin

TIMES_AM = [
    '%s:%s%s' % (h, m, 'am')
    for h in (list(range(6, 12)))
    for m in ('00', '30')
]

TIMES_PM = [
    '%s:%s%s' % (h, m, 'pm')
    for h in (list(range(1, 12)))
    for m in ('00', '30')
]

TIMES = TIMES_AM + TIMES_PM


class RoomReservationSubmit(CreateView):
  model = RoomReservation
  template_name = 'room_reservations/room_reservation.html'
  form_class = RoomReservationForm

  def get_success_url(self, **kwargs):
    if is_TA(self.request.user):
      return reverse_lazy('room_reservations:room-reservation-schedule')
    else:
      return reverse_lazy('room_reservations:room-reservation-submit')

  def get_context_data(self, **kwargs):
    ctx = super(RoomReservationSubmit, self).get_context_data(**kwargs)

    approved_reservations = RoomReservation.objects.filter(status='A')
    reservations = RoomReservation.objects.filter(requester=self.request.user)
    rooms = Room.objects.all()
    approved_reservations_json = serialize('json', approved_reservations)
    rooms_json = serialize('json', rooms)

    ctx['reservations'] = approved_reservations_json
    ctx['requested_reservations'] = reservations
    ctx['rooms_list'] = rooms_json
    ctx['times_list'] = TIMES
    ctx['page_title'] = 'Create Room Reservation' if is_TA(self.request.user) else \
                        'Request Room Reservation'
    ctx['button_label'] = 'Submit'
    return ctx

  def form_valid(self, form):
    room_reservation = form.save(commit=False)
    user_id = self.request.user.id
    room_reservation.requester = User.objects.get(id=user_id)
#    if TrainingAssistant.objects.filter(id=user_id).exists():
#      room_reservation.status = 'A'
    room_reservation.save()
    return super(RoomReservationSubmit, self).form_valid(form)


class RoomReservationUpdate(RoomReservationSubmit, UpdateView):
  def get_context_data(self, **kwargs):
    ctx = super(RoomReservationUpdate, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Edit Reservation'
    ctx['button_label'] = 'Update'
    return ctx


class RoomReservationDelete(RoomReservationSubmit, DeleteView):
  model = RoomReservation


class TARoomReservationList(GroupRequiredMixin, TemplateView):
  model = RoomReservation
  group_required = ['training_assistant']
  template_name = 'room_reservations/ta_list.html'

  def get_context_data(self, **kwargs):
    ctx = super(TARoomReservationList, self).get_context_data(**kwargs)
    reservations = RoomReservation.objects.all()
    ctx['reservations'] = reservations
    return ctx


class RoomReservationSchedule(GroupRequiredMixin, RoomReservationSubmit, TemplateView):
  object = None
  group_required = ['training_assistant']
  template_name = 'room_reservations/schedule.html'


class RoomReservationTVView(TemplateView):
  model = RoomReservation
  template_name = 'room_reservations/tv_page.html'


def weather_api(request):
  ANAHEIM_WEATHER = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%22anaheim%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
  return JsonResponse(requests.get(ANAHEIM_WEATHER).json())


# to be incremented for convenience rather than having to go into room to
# refresh the page
def tv_page_version(request):
  return HttpResponse('0')


def zero_pad(time):
  return '0' + str(time) if time < 10 else str(time)


def tv_page_reservations(request):
  limit = int(request.GET.get('limit', 10))
  offset = int(request.GET.get('offset', 0))
  rooms = Room.objects.all()[offset:limit + offset]
  room_data = []
  for r in rooms:
    reservations = RoomReservation.objects.filter(room=r, date=date.today())
    res = []
    for reservation in reservations:
      hours = reservation.end.hour - reservation.start.hour
      minutes = reservation.end.minute - reservation.start.minute
      intervals = hours * 2 + minutes // 30
      hour = reservation.start.hour
      minute = reservation.start.minute
      for _ in range(intervals):
        time = zero_pad(hour) + ':' + zero_pad(minute)
        res.append({'time': time, 'content': reservation.group})
        if minute == 30:
          minute = 0
          hour += 1
        else:
          minute = 30
    room_data.append({'name': r.name, 'res': res})
  return HttpResponse(json.dumps(room_data))


reservation_modify_status = modify_model_status(RoomReservation, reverse_lazy('room_reservations:ta-room-reservation-list'))
