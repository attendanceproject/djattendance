from collections import namedtuple

from django import template
from aputils.trainee_utils import is_trainee, is_TA
from django.core.urlresolvers import reverse
from graduation.utils import grad_forms
from form_manager.utils import user_forms
from hc.utils import hc_surveys, hc_recommendations


# Type Declarations
def SubMenuItem(name, permission=None, url='#', condition=True):
  return namedtuple('SubMenuItem', 'name permission url condition')(name=name, permission=permission, url=url, condition=condition)


def MenuItem(name, ta_only=[], trainee_only=[], common=[], specific=[]):
  return namedtuple('MenuItem', 'name ta_only trainee_only common specific')(name=name, ta_only=ta_only, trainee_only=trainee_only, common=common, specific=specific)


register = template.Library()


# Helper Functions
def my_reverse(url_pattern):
  if url_pattern != '#' and '/' not in url_pattern:
    return reverse(url_pattern)
  else:
    return url_pattern


def smart_add(url, name):
  path = my_reverse(url)
  return [(path, name)]


# Generates the menu
@register.assignment_tag(takes_context=True)
def generate_menu(context):

  user = context['user']
  if user.is_anonymous():
    return ""
  menu = ""

  # The sidebar menu items, with their permissions and conditions required, should be input here
  attendance_menu = MenuItem(
      name='Attendance',
      ta_only=[
          SubMenuItem(name='View Leave Slips', url='leaveslips:ta-leaveslip-list'),
          SubMenuItem(name='View Service Attendance', url='services:service_hours_ta_view'),
          SubMenuItem(name='Generate Reports', url='reports:generate-reports'),
          SubMenuItem(name='View Trainee Attendance', url='attendance:attendance-submit'),
      ],
      trainee_only=[
          SubMenuItem(name='Absent Trainee Roster', permission='absent_trainee_roster.add_roster', url='absent_trainee_roster:absent_trainee_form', condition=user.has_group(['HC', 'absent_trainee_roster'])),
          SubMenuItem(name='Personal Attendance', url='attendance:attendance-submit', condition=True),
          SubMenuItem(name='Class Roll', permission='attendance.add_roll', url='attendance:class-rolls', condition=user.has_group(['training_assistant', 'attendance_monitors'])),
          SubMenuItem(name='Meal Roll', permission='attendance.add_roll', url='attendance:meal-rolls', condition=user.has_group(['training_assistant', 'attendance_monitors'])),
          SubMenuItem(name='Study Roll', permission='attendance.add_roll', url='attendance:study-rolls', condition=user.has_group(['training_assistant', 'attendance_monitors'])),
          SubMenuItem(name='Class Table', permission='attendance.add_roll', url='attendance:class-table-rolls', condition=user.has_group(['attendance_monitors'])),
          SubMenuItem(name='YPC Roll', permission='attendance.add_roll', url='attendance:ypc-rolls', condition=user.has_group(['attendance_monitors', 'ypc_monitors'])),
          SubMenuItem(name='Audit', permission='attendance.add_roll', url='attendance:audit-rolls', condition=user.has_group(['attendance_monitors'])),
          SubMenuItem(name='Designated Service Hours', permission='services.add_designated_service_hours', url='services:designated_service_hours', condition=user.has_group(['designated_service'])),
      ],
      common=[
          SubMenuItem(name='House Roll', permission='attendance.add_roll', url='attendance:house-rolls', condition=user.has_group(['attendance_monitors', 'HC'])),
          SubMenuItem(name='Team Roll', permission='attendance.add_roll', url='attendance:team-rolls', condition=user.has_group(['attendance_monitors', 'team_monitors'])),
      ])

  discipline_menu = MenuItem(
      name='Discipline',
      common=[
          SubMenuItem(name='Life Studies', url='lifestudies:discipline_list'),
          SubMenuItem(name='Class Notes', url='classnotes:classnotes_list')
      ]
  )

  exam_menu = MenuItem(
      name='Exams',
      ta_only=[
          SubMenuItem(name='Create Exam', permission='exams.add_exam', url='exams:new', condition=user.has_group(['exam_graders', 'training_assistant'])),
          SubMenuItem(name='Manage Exams', permission='exams.add_exam', url='exams:manage', condition=user.has_group(['exam_graders', 'training_assistant'])),
      ],
      trainee_only=[
        SubMenuItem(name="View Graded Exams", url='exams:taken', condition=context['exams_taken']),
      ]

  )

  requests_menu = MenuItem(
      name='Requests',
      ta_only=[
          SubMenuItem(name='Room Reservation', url='room_reservations:ta-room-reservation-list'),
          SubMenuItem(name='Audio', url='audio:ta-audio-home'),
      ],
      trainee_only=[
          SubMenuItem(name='Room Reservation', url='room_reservations:room-reservation-submit'),
          SubMenuItem(name='Audio', url='audio:audio-home'),
      ],
      common=[
          SubMenuItem(name='Announcements', url='announcements:announcement-request-list'),
          SubMenuItem(name='Web Access', url='web_access:web_access-list'),
          SubMenuItem(name='Maintenance', url='house_requests:maintenance-list'),
          SubMenuItem(name='Linens', url='house_requests:linens-list', condition=user.has_group(['training_assistant', 'HC', 'linens'])),
          SubMenuItem(name='Framing', url='house_requests:framing-list'),
      ]
  )

  misc_menu = MenuItem(
      name="Misc",
      common=[
          SubMenuItem(name='Bible Reading Tracker', url='bible_tracker:index'),
          SubMenuItem(name='Class Files', url='classes:index'),
      ],
      ta_only=[
          SubMenuItem(name='Daily Announcements', url='announcements:announcement-list'),
          SubMenuItem(name='Designated Services Viewer', url='services:designated_services_viewer')
          # SubMenuItem(name='HC Forms Admin', url='hc:hc-admin'),
          # SubMenuItem(name='Manage Custom Forms', url='fobi.dashboard')
      ],
      trainee_only=[
          SubMenuItem(name='View Read Announcements', url='announcements:announcements-read'),
      ],
      specific=[
          SubMenuItem(name='Service Scheduling', permission='services.add_service', url='services:services_view', condition=user.has_group(['service_schedulers'])),
          SubMenuItem(name='Badges', permission='badges.add_badge', url='badges:badges_list', condition=user.has_group(['badges'])),
          SubMenuItem(name='Meal Seating', permission='meal_seating.add_table', url='meal_seating:new-seats', condition=user.has_group(['kitchen'])),
          SubMenuItem(name='Seating Chart', permission='seating.add_chart', url='seating:chart_list', condition=user.has_group(['attendance_monitors'])),
          SubMenuItem(name='Audio Upload', permission='audio.add_audiofile', url='audio:audio-upload', condition=user.has_group(['av'])),
      ]
  )

  hc_forms = []
  if hc_surveys():
    hc_forms.append(SubMenuItem(name='HC Surveys', permission='hc.add_survey', url='hc:hc-survey', condition=user.has_group(['HC'])))
  if hc_recommendations():
    hc_forms.append(SubMenuItem(name='HC Recommendations', permission='hc.add_recommendation', url='hc:hc-recommendation', condition=user.has_group(['HC'])))

  HC_menu = MenuItem(
      name="HC",
      trainee_only=hc_forms,
      common=[]
  )

  grad_menu = MenuItem(
      name="Grad",
      specific=[
          SubMenuItem(name='Grad Admin', permission='graduation.add_gradadmin', url='graduation:grad-admin', condition=user.has_group(['training_assistant'])),
      ],
      trainee_only=[SubMenuItem(name=f.menu_title(), url=f.get_absolute_url()) for f in grad_forms(user)]
  )

  # For every 'current' item that needs to appear in the side-bar, ie exams to be taken, iterim intentions form, exit interview, etc, the context variable needs to be added to the context, and the menu item can be added here as follows
  current_menu = MenuItem(
      name='Current',
      trainee_only=[
          SubMenuItem(name="Take Exam", url='exams:list', condition=context['exams_available']),
      ] + [SubMenuItem(name=pf.name, url='/forms/view/' + pf.slug) for pf in user_forms(user)],
  )

  user_menu = [attendance_menu, discipline_menu, requests_menu, exam_menu, misc_menu, HC_menu, current_menu, grad_menu]

  # check for usertype TA and only in one group, maintenance or kitchen
  if user.type == 'T' and user.has_group(['facility_maintenance']) and user.groups.all().count() == 1:
    user_menu = []

  for menu_item in user_menu:
    items = []
    if menu_item.common:
      for sub_item in menu_item.common:
        if sub_item.condition:
          items += smart_add(sub_item.url, sub_item.name)
    if menu_item.ta_only:
      if is_TA(user):
        for sub_item in menu_item.ta_only:
          if sub_item.condition:
            items += smart_add(sub_item.url, sub_item.name)
    if menu_item.trainee_only:
      if is_trainee(user):
        for sub_item in menu_item.trainee_only:
          if sub_item.condition:
            items += smart_add(sub_item.url, sub_item.name)
    if menu_item.specific:
      for specific_perm_item in menu_item.specific:
          if specific_perm_item.condition:
            items += smart_add(specific_perm_item.url, specific_perm_item.name)
    if items:
      menu += """<li class="dropdown">
        <span class="triangle-up"></span>
        <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">
          {0}
        </a><ul class="dropdown-menu"><li class="spacer"></li>""".format(menu_item.name)
      for (path, name) in sorted(items, key=lambda i: i[1]):
        if name == '|':
          menu += "<li role=\"separator\" class=\"divider\"></li>"
        else:
          menu += "<li><a href=\"" + path + "\">" + name + "</a></li>"
      menu += "</ul>"
  return menu
