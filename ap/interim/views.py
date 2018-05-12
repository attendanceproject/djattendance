from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from accounts.models import Trainee
from aputils.trainee_utils import trainee_from_user
from interim.models import InterimIntentions, InterimItinerary, InterimIntentionsAdmin
from interim.forms import InterimIntentionsForm, InterimItineraryForm, InterimIntentionsAdminForm
from terms.models import Term

from braces.views import GroupRequiredMixin

from dateutil import parser
from datetime import datetime, timedelta


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
    commments_list = data.pop('comments')
    InterimItinerary.objects.filter(interim_intentions=interim_intentions).delete()

    for index in range(len(start_list)):
      itin = InterimItinerary()
      itin.interim_intentions = interim_intentions
      itin.start = parser.parse(start_list[index])
      itin.end = parser.parse(end_list[index])
      itin.comments = commments_list[index]
      itin.save()

  def get_context_data(self, **kwargs):
    ctx = super(InterimIntentionsView, self).get_context_data(**kwargs)
    admin, created = InterimIntentionsAdmin.objects.get_or_create(term=Term.current_term())
    interim_itineraries_forms = []
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
    ctx['admin'] = admin

    return ctx


class InterimIntentionsAdminView(UpdateView, GroupRequiredMixin):
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

    def merge_entries(d, key1, key2, newkey, sep=' '):
      try:
        d[newkey] = unicode(d[key1]) + unicode(sep) + unicode(d[key2])
        del d[key1]
        del d[key2]
        return 1
      except KeyError:
        return 0

    trainees = Trainee.objects.values('firstname', 'lastname', 'current_term',
                                      'team__name', 'locality__city__name',
                                      'locality__city__state', 'id')
    for t in trainees:
      t['intention'] = InterimIntentions.objects.filter(trainee__id=t['id'], admin__term=term).first()
      merge_entries(t, 'locality__city__name', 'locality__city__state', 'locality', sep=', ')
      merge_entries(t, 'firstname', 'lastname', 'name')

    ctx['trainees'] = trainees
    ctx['page_title'] = 'Interim Intentions Report'
    return ctx
