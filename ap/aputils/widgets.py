from django.urls import reverse
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.templatetags.admin_static import static
from django.forms.widgets import TimeInput, DateInput, DateTimeInput, SelectMultiple
from django_select2.forms import Select2MultipleWidget

from services.serializers import ServiceCalendarSerializer
from rest_framework.renderers import JSONRenderer
from datetime import date


class DatePicker(DateInput):
  format = '%m/%d/%Y'

  def __init__(self, *args, **kwargs):
    kwargs['attrs'] = {'class': 'datepicker'}
    super(DatePicker, self).__init__(*args, **kwargs)

  class Media:
    js = (
        'js/datepicker.js',
    )

class DatetimePicker(DateTimeInput):
  format = '%m/%d/%Y %I:%M %p'

  def __init__(self, *args, **kwargs):
    kwargs['attrs'] = {'class': 'datetimepicker'}
    kwargs['attrs']['placeholder'] = "01/01/2018 03:45 PM"
    super(DatetimePicker, self).__init__(*args, **kwargs)

  class Media:
    js = (
        'js/datetimepicker.js',
    )

class TimePicker(TimeInput):
  format = '%I:%M %p'

  def __init__(self, *args, **kwargs):
    kwargs['attrs'] = {'class': 'timepicker'}
    super(TimePicker, self).__init__(*args, **kwargs)

  class Media:
    js = (
        'js/timepicker.js',
    )

class MultipleSelectFullCalendar(SelectMultiple):
  def __init__(self, queryset, name, attrs=None, choices=()):
    self.queryset = queryset
    self.name = name
    super(MultipleSelectFullCalendar, self).__init__(attrs, choices)

  def render(self, name, value, attrs=None):
    # print name, value, choices, self.choices
    services = JSONRenderer().render(ServiceCalendarSerializer(self.queryset, many=True).data).decode('utf-8')
    selected = ",".join(str(x) for x in value) if value is not None else ""
    categories = self.queryset.aggregate(count=Count('category', distinct=True))
    context = {'services': services, 'selected': selected, 'categories': categories}
    additional = render_to_string('MultipleSelectFullCalendar.html', context)
    return additional + super(MultipleSelectFullCalendar, self).render(name=name, value=value, attrs=attrs)

  class Media:
    js = (
      'js/fullcalendar_init.js',
    )


class PlusSelect2MultipleWidget(Select2MultipleWidget):
  def render(self, name, value, attrs=None, choices=()):
    output = super(PlusSelect2MultipleWidget, self).render(name, value, attrs, choices)
    link = []
    rel_to = self.choices.queryset.model
    info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
    related_url = reverse('admin:%s_%s_add' % info, current_app='admin') + '?_to_field=id&amp;_popup=1'
    link.append('<a href="%s" class="related-widget-wrapper-link add-related" id="add_id_%s"> ' % (related_url, name))
    link.append('<img src="%s" width="10" height="10" alt="%s"/></a>'
                % (static('admin/img/icon_addlink.gif'), _('Add Another')))
    return output + mark_safe(''.join(link))
