import cStringIO as StringIO
import xhtml2pdf.pisa as pisa
import time
import functools
import os
from cgi import escape
from datetime import date, datetime

from django.template.defaulttags import register
from django.template.loader import get_template
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages

from .decorators import group_required
# !! IMPORTANT: Keep this file free from any model imports to avoid cyclical dependencies!!


def ensure_date(d):
  if isinstance(d, datetime):
    return d.date()
  return d


def ensure_datetime(d):
  if isinstance(d, date):
    return datetime(d.year, d.month, d.day)
  return d


class RequestMixin(object):
  @property
  def requester_name(self):
    return self.get_trainee_requester().full_name if self.get_trainee_requester() else ''


class OverwriteStorage(FileSystemStorage):
  """
  Removes a duplicate file before storing because otherwise Django will just
  add random letters to the end of the filename.
  """

  def get_valid_name(self, name):
    return name

  def get_available_name(self, name, max_length):
    if self.exists(name):
      os.remove(os.path.join(self.location, name))
    return super(OverwriteStorage, self).get_available_name(name, max_length)


def modify_model_status(model, url):
  @group_required(['training_assistant'], raise_exception=True)
  def modify_status(request, status, id, message_func=None):
    obj = get_object_or_404(model, pk=id)
    obj.status = status
    obj.save()
    if message_func:
      message = message_func(obj)
    else:
      message = "%s's %s was %s" % (obj.requester_name, obj._meta.verbose_name, obj.get_status_display())
    messages.add_message(request, messages.SUCCESS, message)
    return redirect(url)
  return modify_status


def memoize(obj):
  cache = obj.cache = {}

  @functools.wraps(obj)
  def memoizer(*args, **kwargs):
      key = str(args) + str(kwargs)
      if key not in cache:
          cache[key] = obj(*args, **kwargs)
      return cache[key]
  return memoizer


def link_callback(uri, rel):
  """
  Convert HTML URIs to absolute system paths so xhtml2pdf can access those
  resources
  """
  # use short variable names
  sUrl = settings.STATIC_URL      # Typically /static/
  sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
  mUrl = settings.MEDIA_URL       # Typically /static/media/
  mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

  # convert URIs to absolute system paths
  if uri.startswith(mUrl):
    path = os.path.join(mRoot, uri.replace(mUrl, ""))
  elif uri.startswith(sUrl):
    path = os.path.join(sRoot, uri.replace(sUrl, ""))
  else:
    return uri  # handle absolute uri (ie: http://some.tld/foo.png)

  # make sure that file exists
  if not os.path.isfile(path):
    raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))
  return path


def render_to_pdf(template_src, context_dict):
  template = get_template(template_src)
  html = template.render(context=context_dict)
  result = StringIO.StringIO()

  pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result, link_callback=link_callback)
  if not pdf.err:
    return HttpResponse(result.getvalue(), content_type='application/pdf')
  return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


COMMA_REGEX = r'^{0},|,{0},|,{0}$|^{0}$'


def comma_separated_field_is_in_regex(list):
  regs = []
  for item in list:
    regs.append(COMMA_REGEX.format(item))
  reg_str = '|'.join(regs)

  return reg_str


@register.filter
def get_range(value, start=0):
  return range(start, value)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_essay_unique_id(section_id, forloop_counter):
    return int(section_id) + int(forloop_counter)


def sorted_user_list_str(users):
  return ', '.join([u.full_name for u in users.order_by('firstname', 'lastname')])


@register.filter
def get_index(lst, index):
    return lst[index]


# Search for item in a list
@register.filter
def lookup(list, key):
  for el in list:
    if el == key:
      return el
  return None


WEEKDAY_CODE = {
    0: 'M',
    1: 'T',
    2: 'W',
    3: 'Th',
    4: 'F',
    5: 'S',
    6: 'LD',
}


@register.filter
def weekday_code(day):
  return WEEKDAY_CODE[day]


WEEKDAY_CODES = (
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat',
    'LD',
)


WEEKDAYS = (
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Lord\'s Day',
)


@register.filter
def get_weekday_codes(start=0):
    return WEEKDAY_CODES[start:] + WEEKDAY_CODES[:start]


@register.filter
def weekday_name(day):
  return dict(enumerate(WEEKDAYS))[day]


@register.filter
def worker_list(workers):
  return ', '.join([w.full_name for w in workers])


@register.filter
def input_worker_list(workers):
  return ','.join([w.full_name for w in workers])


@register.filter
def input_workerID_list(workers):
  return ','.join([str(w.id) for w in workers])


# Timer decorator
def timeit(method):
  def timed(*args, **kw):
    ts = time.time()
    result = method(*args, **kw)
    te = time.time()

    print '%r %2.2f sec' % (method.__name__, te - ts)
    return result

  return timed


class timeit_inline(object):
  def __init__(self, title=""):
    self.title = title

  def start(self):
    print self.title
    self.ts = time.time()

  def end(self):
    self.te = time.time()
    print '%s %2.2f sec' % (self.title, self.te - self.ts)
