from collections import namedtuple
from datetime import date

from aputils.trainee_utils import trainee_from_user
from attendance.utils import Period
from classnotes.models import Classnotes
from django import template
from django.core.urlresolvers import reverse
from django.db.models import Q
from leaveslips.models import IndividualSlip
from lifestudies.models import Discipline
from terms.models import Term


# code structure copied from aputils/templatetags/smart_menu.py
# TODO: remove use of namedtuple here and in smart_menu.
# We don't really gain anything from it and Python is an object-oriented language.


def Panel(name, num, url):
  return namedtuple('Panel', 'name num url')(name=name, num=num, url=url)


register = template.Library()


# Generates all the panels
@register.assignment_tag(takes_context=True)
def generate_panels(context):
  user = context['user']
  if user.is_anonymous():
    return ""

  ls = Discipline.objects.filter(trainee=user)
  num_ls = 0
  for l in ls:
    num_ls = num_ls + l.get_num_summary_due()

  lifestudies_panel = Panel(
      name='Life Studies',
      # to temp fix -1 due life studies, TODO fix -1 summaries needed
      # num= num_ls
      num=num_ls if num_ls > 0 else 0,
      url=reverse('lifestudies:discipline_list'),
  )

  classnotes_panel = Panel(
      name='Class Notes',
      num=Classnotes.objects.filter(Q(trainee=user) & ~Q(status='A')).count(),
      url=reverse('classnotes:classnotes_list')
  )

  # try and except to accomodate for superuser
  p = Period(Term.current_term()).period_of_date(date.today())
  uet = uea = 0
  try:
    att_rcd = trainee_from_user(user).get_attendance_record(p)
    for att in att_rcd:
      if att['attendance'] in ['A', 'T']:
        excused = filter(lambda a: a['start'] == att['start'], att_rcd)
        if len(excused) < 2:
          if att['attendance'] == 'A':
            uea += 1
          elif att['attendance'] == 'T':
            uet += 1
  except AttributeError:
    pass

  unexcusedtardies_panel = Panel(
      name='Unexcused Tardies',
      num=uet,
      url=reverse('attendance:attendance-submit')
  )
  unexcusedabsences_panel = Panel(
      name='Unexcused Absences',
      num=uea,
      url=reverse('attendance:attendance-submit')
  )

  ls_pending = 0
  ls_p = IndividualSlip.objects.filter(trainee=user, status='P')
  ls_pending = sum([1 if p in slip.periods else 0 for slip in ls_p])

  leaveslips_panel = Panel(
      name='Leave Slips Pending',
      num=ls_pending,
      url=reverse('attendance:attendance-submit')
  )

  panels = [leaveslips_panel, unexcusedtardies_panel, unexcusedabsences_panel, lifestudies_panel, classnotes_panel]

  return panels
