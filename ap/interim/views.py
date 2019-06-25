from datetime import datetime, timedelta

from accounts.models import Trainee
from aputils.trainee_utils import trainee_from_user
from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from interim.forms import (InterimIntentionsAdminForm, InterimIntentionsForm,
                           InterimItineraryForm)
from interim.models import (InterimIntentions, InterimIntentionsAdmin,
                            InterimItinerary)
from terms.models import Term


class InterimIntentionsView(UpdateView):
  model = InterimIntentions
  template_name = 'interim/interim_intentions.html'
  form_class = InterimIntentionsForm

  def get_object(self, queryset=None):
    trainee = trainee_from_user(self.request.user)
    admin, created = InterimIntentionsAdmin.objects.get_or_create(term=Term.current_term())
    int_int, created = InterimIntentions.objects.get_or_create(trainee=trainee_from_user(self.request.user), admin=admin)

    if created:
      int_int.email = trainee.email
      int_int.cell_phone = trainee.meta.phone
      int_int.home_locality = trainee.locality.city.name
      int_int.home_address = trainee.meta.address.address1
      int_int.home_city = trainee.meta.address.city.name
      int_int.home_state = trainee.meta.address.city.get_state_display()
      int_int.home_zip = trainee.meta.address.zip_code
      int_int.save()

    return int_int

  def form_valid(self, form):
    self.update_interim_itinerary(interim_intentions=self.get_object(), data=self.request.POST.copy())
    return super(InterimIntentionsView, self).form_valid(form)

  def update_interim_itinerary(self, interim_intentions, data):
    start_list = data.pop('start')
    end_list = data.pop('end')
    comments_list = data.pop('comments')
    itins = []

    for index in range(len(start_list)):
<<<<<<< HEAD
      itins.append(InterimItineraryForm(data={
        'start': start_list[index],
        'end': end_list[index],
        'comments': commments_list[index],
        'interim_intentions': interim_intentions})
      )
=======
      print(start_list[index] + " to " + end_list[index] + ": " + comments_list[index]);
      itins.append(InterimItineraryForm(data={'start':start_list[index], 'end':end_list[index], 'comments':comments_list[index], 'interim_intentions': interim_intentions}))
>>>>>>> dev
    if all(f.is_valid() for f in itins):
      InterimItinerary.objects.filter(interim_intentions=interim_intentions).delete()
      for itin in itins:
        itobj = itin.save(commit=False)
        itobj.interim_intentions = interim_intentions
        itobj.save()
    return itins

  def get_context_data(self, **kwargs):
    ctx = super(InterimIntentionsView, self).get_context_data(**kwargs)
    admin, created = InterimIntentionsAdmin.objects.get_or_create(term=Term.current_term())
    interim_itineraries_forms = []
    if self.request.method == 'POST':
      interim_itineraries_forms = self.update_interim_itinerary(interim_intentions=self.get_object(), data=self.request.POST.copy())
    elif self.request.method == 'GET':
      interim_itineraries = InterimItinerary.objects.filter(interim_intentions=self.get_object()).order_by('start')
      if interim_itineraries.count() == 0:
        interim_itineraries_forms.append(InterimItineraryForm())
      else:
        for itin in interim_itineraries:
          interim_itineraries_forms.append(InterimItineraryForm(instance=itin))
    ctx['button_label'] = 'Submit'
    ctx['page_title'] = 'Interim Intentions'
    ctx['itinerary_forms'] = interim_itineraries_forms
    ctx['interim_start'] = Term.current_term().end + timedelta(days=1)
    ctx['interim_end'] = admin.term_begin_date - timedelta(days=1)
    ctx['admin'] = admin

    return ctx


class InterimIntentionsAdminView(GroupRequiredMixin, UpdateView):
  model = InterimIntentionsAdmin
  form_class = InterimIntentionsAdminForm
  template_name = 'interim/interim_intentions_admin.html'
  group_required = ['training_assistant']

  def get_object(self, queryset=None):
    obj, created = self.model.objects.get_or_create(term=Term.current_term())
    return obj

  def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    return super(InterimIntentionsAdminView, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    obj = self.get_object()
    data = self.request.POST.copy()
    obj.open_time = datetime.strptime(data['open_time'], "%m/%d/%Y %I:%M %p")
    obj.close_time = datetime.strptime(data['close_time'], "%m/%d/%Y %I:%M %p")
    obj.date_1yr_return = datetime.strptime(data['date_1yr_return'], "%m/%d/%Y %I:%M %p")
    obj.date_2yr_return = datetime.strptime(data['date_2yr_return'], "%m/%d/%Y %I:%M %p")
    obj.term_begin_date = datetime.strptime(data['term_begin_date'], "%m/%d/%Y")
    obj.earliest_arrival_date = datetime.strptime(data['earliest_arrival_date'], "%m/%d/%Y")
    obj.save()
    return super(InterimIntentionsAdminView, self).get(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    ctx = super(InterimIntentionsAdminView, self).get_context_data(**kwargs)
    ctx['page_title'] = "Interim Intentions Admin"
    ctx['button_label'] = 'Save'
    return ctx


class InterimIntentionsTAView(TemplateView, GroupRequiredMixin):
  template_name = 'interim/interim_intentions_ta_view.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    ctx = super(InterimIntentionsTAView, self).get_context_data(**kwargs)
    term = Term.current_term()

    def merge_locality_entries(d, sep=' '):
      prefix = 'locality__city__'
      try:
        d['locality'] = str(d[prefix + 'name']) + str(sep)
        if not d[prefix + 'state']:
          d['locality'] += str(d[prefix + 'country'])
        else:
          d['locality'] += str(d[prefix + 'state'])
        del d[prefix + 'name']
        del d[prefix + 'state']
        del d[prefix + 'country']
        return 1
      except KeyError:
        return 0

    def merge_entries(d, key1, key2, newkey, sep=' '):
      try:
        d[newkey] = str(d[key1]) + str(sep) + str(d[key2])
        del d[key1]
        del d[key2]
        return 1
      except KeyError:
        return 0

    trainees = Trainee.objects.values('firstname', 'lastname', 'current_term',
                                      'team__name', 'locality__city__name', 'locality__city__state',
                                      'locality__city__country', 'id')
    for t in trainees:
      t['intention'] = InterimIntentions.objects.filter(trainee__id=t['id'], admin__term=term).first()
      merge_locality_entries(t, sep=', ')
      merge_entries(t, 'firstname', 'lastname', 'name')

    ctx['trainees'] = trainees
    ctx['page_title'] = 'Interim Intentions Report'
    return ctx


class InterimIntentionsCalendarView(TemplateView, GroupRequiredMixin):
  template_name = 'interim/interim_intentions_calendar_view.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    ctx = super(InterimIntentionsCalendarView, self).get_context_data(**kwargs)
    term = Term.current_term()

    interim_start = term.end + timedelta(days=1)
    if not InterimIntentionsAdmin.objects.get(term=term).date_1yr_return or not InterimIntentionsAdmin.objects.get(term=term).date_2yr_return:
      interim_end = interim_start + timedelta(days=1)
      ctx['subtitle'] = "Please enter the return dates for next term."
    else:
      date_1 = InterimIntentionsAdmin.objects.get(term=term).date_1yr_return
      date_2 = InterimIntentionsAdmin.objects.get(term=term).date_2yr_return
      interim_end = date_2.date() if (date_2 >= date_1) else date_1.date();

    ctx['interim_length'] = (interim_end - interim_start).days + 1
    ctx['date_list'] = [interim_start + timedelta(days=x) for x in range(0, ctx['interim_length'])]

    ctx['trainees'] = Trainee.objects.values('firstname', 'lastname', 'id')

    for t in ctx['trainees']:
      t['name'] = str(t['firstname'] + ' ' + t['lastname'])
      t['intention'] = InterimIntentions.objects.filter(trainee__id=t['id'], admin__term=term).first()

    ctx['page_title'] = 'Interim Calendar Report'
    return ctx
