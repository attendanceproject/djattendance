# import xlwt
# from openpyxl import Workbook
import io, xlsxwriter

from datetime import datetime, timedelta

from accounts.models import Trainee
from aputils.trainee_utils import trainee_from_user
from braces.views import GroupRequiredMixin
from dateutil import parser
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.http import HttpResponse
from interim.forms import (InterimIntentionsAdminForm, InterimIntentionsForm,
                           InterimItineraryForm)
from interim.models import (InterimIntentions, InterimIntentionsAdmin,
                            InterimItinerary, POST_INTENT_CHOICES)
from terms.models import Term


term = Term.current_term()


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
      print(start_list[index] + " to " + end_list[index] + ": " + comments_list[index]);
      itins.append(InterimItineraryForm(data={'start':start_list[index], 'end':end_list[index], 'comments':comments_list[index], 'interim_intentions': interim_intentions}))
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

    def merge_locality_entries(d, sep=' '):
      prefix = 'locality__city__'
      try:
        d['locality'] = unicode(d[prefix + 'name']) + unicode(sep)
        if not d[prefix + 'state']:
          d['locality'] += unicode(d[prefix + 'country'])
        else:
          d['locality'] += unicode(d[prefix + 'state'])
        del d[prefix + 'name']
        del d[prefix + 'state']
        del d[prefix + 'country']
        return 1
      except KeyError:
        return 0

    def merge_entries(d, key1, key2, newkey, sep=' '):
      try:
        d[newkey] = unicode(d[key1]) + unicode(sep) + unicode(d[key2])
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


def export_interim_intentions_xls(request):
  output = io.BytesIO() # in-memory output file for workbook

  wb = xlsxwriter.Workbook(output)
  ws = wb.add_worksheet()

  # formatting - colors from UI toolkit but not proportional
  header_format = wb.add_format({'align': 'center', 'valign': 'vcenter', 'rotation': '90', 'text_wrap': True, 'bg_color': '#ffdb77', 'border': 1})
  red_header_format = wb.add_format({'align': 'center', 'valign': 'vcenter', 'rotation': '90', 'text_wrap': True, 'bg_color': '#f69d74', 'border': 1})
  blue_header_format = wb.add_format({'align': 'center', 'valign': 'vcenter', 'rotation': '90', 'text_wrap': True, 'bg_color': '#a6c4d1', 'border': 1})
  ws.freeze_panes(1, 2)

  # sizing cells
  ws.set_row(0, 150)
  ws.set_column(0, 0, 4.2)
  ws.set_column(1, 1, 23)
  ws.set_column(2, 3, 3.5)
  ws.set_column(4, 4, 20)
  ws.set_column(5, 5, 33)
  ws.set_column(6, 17, 4.2)
  ws.set_column(18, 18, 55)

  row_num = 0
  columns = ['NAME', 'GENDER', 'TERM', 'LOCALITY', 'TEAM',
            'RETURNING TO FTTA (1st-3rd)', 'NOT RETURNING (1st-3rd)',
            'UNDECIDED (1st-3rd)'] + [x[1] for x in POST_INTENT_CHOICES]
  columns.pop() # remove last "None" option
  columns.append("Notes")

  # excel headers
  ws.write(row_num, 0, None, header_format)
  for col_num, column_title in enumerate(columns, 1):
    switch_format = header_format
    if col_num in range(6, 9):
      switch_format = red_header_format
    elif col_num in range(9, 18):
      switch_format = blue_header_format
    ws.write(row_num, col_num, column_title, switch_format)

  # trainee content
  plain_format = wb.add_format({'border': 1})
  plain_center_format = wb.add_format({'align': 'center', 'border': 1})
  red_format = wb.add_format({'align': 'center', 'bg_color': '#f69d74', 'border': 1})
  blue_format = wb.add_format({'align': 'center', 'bg_color': '#a6c4d1', 'border': 1})

  trainees = Trainee.objects.values('firstname', 'lastname', 'gender', 'current_term',
                                    'team__name', 'locality__city__name', 'id')
  row_num = 1
  inter_plans = dict([('R', 6), ('N', 7), ('U', 8)])
  post_plans = dict([('USC', 9), ('OCC', 10), ('LSM', 11), ('BFA', 12), ('OTH', 13),
                       ('XB', 14), ('JOB', 15), ('SCH', 16), ('UND', 17)])
  for t in trainees:
    intention = InterimIntentions.objects.filter(trainee__id=t['id'], admin__term=term).first()

    # default entries
    ws.write(row_num, 0, row_num, plain_center_format)
    ws.write(row_num, 1, t['firstname'] + " " + t['lastname'], plain_format)
    ws.write(row_num, 2, t['gender'], plain_center_format)
    ws.write(row_num, 3, t['current_term'], plain_center_format)
    ws.write(row_num, 4, t['locality__city__name'], plain_format)
    ws.write(row_num, 5, t['team__name'], plain_format)
    for i in range(6, 9):
      ws.write(row_num, i, None, red_format)
    for i in range(9, 18):
      ws.write(row_num, i, None, blue_format)
    ws.write(row_num, 18, None, plain_format)

    # more specific entries
    if intention:
      if intention.intent != 'G':
        ws.write(row_num, inter_plans[intention.intent], 'x', red_format)
      if intention.post_training_intentions not in ["NON", ""]:
        ws.write(row_num, post_plans[intention.post_training_intentions], 'x', blue_format)
      ws.write(row_num, 18, intention.post_intent_comments, plain_format)

    row_num = row_num + 1

  wb.close()
  output.seek(0) # rewinding the buffer

  response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
  response['Content-Disposition'] = 'attachment; filename=Interim-{t}.xlsx'.format(
    t = term.season + str(term.year)
  )

  return response


class InterimIntentionsCalendarView(TemplateView, GroupRequiredMixin):
  template_name = 'interim/interim_intentions_calendar_view.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    ctx = super(InterimIntentionsCalendarView, self).get_context_data(**kwargs)

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
      t['name'] = unicode(t['firstname'] + ' ' + t['lastname'])
      t['intention'] = InterimIntentions.objects.filter(trainee__id=t['id'], admin__term=term).first()

    ctx['page_title'] = 'Interim Calendar Report'
    return ctx
