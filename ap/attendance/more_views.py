from ap.base_datatable_view import BaseDatatableView, DataTableViewerMixin
from attendance.models import Roll
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.views.generic.base import TemplateView
from leaveslips.models import GroupSlip, IndividualSlip
from schedules.models import Event, Schedule
from terms.models import Term


class DataTableViewer(DataTableViewerMixin, TemplateView):
  template_name = "data/viewer.html"


class RollsJSON(BaseDatatableView):
  model = Roll
  fields = ['id', 'trainee', 'event', 'event.id', 'date', 'status', 'finalized', 'submitted_by']
  columns = fields
  order_columns = fields
  max_display_length = 200
  term = Term.current_term()

  def filter_queryset(self, qs):
    qs = qs.filter(date__gte=self.term.start, date__lte=self.term.end)
    search = self.request.GET.get(u'search[value]', None)
    qs_params = Q()
    ret = qs.none()
    if search:
      for exp in search.split():
        try:
          q = Q(trainee__firstname__icontains=exp) | Q(trainee__lastname__icontains=exp) | Q(id__icontains=exp) | \
              Q(event__id__icontains=exp) | Q(event__name__icontains=exp) | Q(date__icontains=exp) | Q(status__icontains=exp)
          qs_params = qs_params & q if q else qs_params

        except ValueError:
          continue

      ret = ret | qs.filter(qs_params).distinct()
      return ret
    else:
      return qs


class RollsViewer(DataTableViewer):
  DataTableView = RollsJSON
  source_url = reverse_lazy('attendance:rolls-json')

  def get_context_data(self, **kwargs):
    ctx = super(RollsViewer, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Rolls Viewer'
    return ctx


class LeaveSlipsJSON(BaseDatatableView):
  model = IndividualSlip
  fields = ['id', 'trainee', 'rolls', 'status', 'TA', 'type']
  columns = fields
  order_columns = fields
  max_display_length = 200
  which_url = 'get_admin_url'
  term = Term.current_term()

  def filter_queryset(self, qs):
    qs = qs.filter(rolls__date__gte=self.term.start, rolls__date__lte=self.term.end)
    search = self.request.GET.get(u'search[value]', None)
    qs_params = Q()
    ret = qs.none()
    if search:
      for exp in search.split():
        try:
          q = Q(trainee__firstname__icontains=exp) | Q(trainee__lastname__icontains=exp) | Q(id__icontains=exp) | \
              Q(type__icontains=exp) | Q(rolls__event__name__icontains=exp) | Q(rolls__event__id__icontains=exp) | Q(rolls__id__icontains=exp)
          qs_params = qs_params & q if q else qs_params

        except ValueError:
          continue

      ret = ret | qs.filter(qs_params).distinct()
      return ret
    else:
      return qs


class LeaveSlipViewer(DataTableViewer):
  DataTableView = LeaveSlipsJSON
  source_url = reverse_lazy('attendance:leaveslips-json')

  def get_context_data(self, **kwargs):
    ctx = super(LeaveSlipViewer, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Leave Slips Viewer'
    return ctx


class GroupSlipsJSON(BaseDatatableView):
  model = GroupSlip
  columns = ['id', 'trainee', 'submitted', 'trainees', 'description', 'status', 'service_assignment', 'start', 'end']
  order_columns = ['id', 'trainee', 'submitted', '', 'description', 'status', 'service_assignment', 'start', 'end']
  max_display_length = 200
  which_url = 'get_admin_url'
  term = Term.current_term()

  def filter_queryset(self, qs):
    qs = qs.filter(start__gte=self.term.start, end__lte=self.term.end)
    search = self.request.GET.get(u'search[value]', None)
    qs_params = Q()
    ret = qs.none()
    if search:
      for exp in search.split():
        try:
          q = Q(id__icontains=exp) | Q(service_assignment__service__name__icontains=exp)
          qs_params = qs_params & q if q else qs_params

        except ValueError:
          continue

      ret = ret | qs.filter(qs_params).distinct()
      return ret
    else:
      return qs


class GroupSlipViewer(DataTableViewer):
  DataTableView = GroupSlipsJSON
  source_url = reverse_lazy('attendance:groupslips-json')

  def get_context_data(self, **kwargs):
    ctx = super(GroupSlipViewer, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Group Slips Viewer'
    return ctx


class EventsJSON(BaseDatatableView):
  model = Event
  fields = ['id', 'name', 'weekday', 'type', 'monitor', 'start', 'end', 'chart']
  columns = fields
  order_columns = fields
  max_display_length = 200

  def filter_queryset(self, qs):
    search = self.request.GET.get(u'search[value]', None)
    qs_params = Q()
    ret = qs.none()
    if search:
      for exp in search.split():
        try:
          q = Q(id__icontains=exp) | Q(name__icontains=exp) | Q(weekday__icontains=exp) | \
              Q(type__icontains=exp) | Q(monitor__icontains=exp) | Q(start__icontains=exp) | Q(end__icontains=exp)
          qs_params = qs_params & q if q else qs_params

        except ValueError:
          continue

      ret = ret | qs.filter(qs_params).distinct()
      return ret
    else:
      return qs


class EventsViewer(DataTableViewer):
  DataTableView = EventsJSON
  source_url = reverse_lazy('attendance:events-json')

  def get_context_data(self, **kwargs):
    ctx = super(EventsViewer, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Events Viewer'
    return ctx


class SchedulesJSON(BaseDatatableView):
  model = Schedule
  columns = ['id', 'name', 'comments', 'events', 'trainees', 'weeks', 'query_filter', 'priority']
  order_columns = ['id', 'name', 'comments', 'query_filter', '', '', 'weeks', 'priority']
  max_display_length = 200

  def filter_queryset(self, qs):
    search = self.request.GET.get(u'search[value]', None)
    qs_params = Q()
    ret = qs.none()
    if search:
      for exp in search.split():
        try:
          q = Q(id__icontains=exp) | Q(name__icontains=exp) | Q(events__id__icontains=exp) | \
              Q(events__name__icontains=exp) | Q(trainees__firstname__icontains=exp) | Q(trainees__lastname__icontains=exp)
          qs_params = qs_params & q if q else qs_params

        except ValueError:
          continue

      ret = ret | qs.filter(qs_params).distinct()
      return ret
    else:
      return qs


class SchedulesViewer(DataTableViewer):
  DataTableView = SchedulesJSON
  source_url = reverse_lazy('attendance:schedules-json')

  def get_context_data(self, **kwargs):
    ctx = super(SchedulesViewer, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Schedules Viewer'
    return ctx
