from collections import namedtuple
from django import template
from django.core.urlresolvers import reverse

from web_access.models import WebRequest
from announcements.models import Announcement
from accounts.models import *
from audio.models import AudioRequest
from house_requests.models import *
from room_reservations.models import RoomReservation
from leaveslips.models import IndividualSlip, GroupSlip
from lifestudies.models import Summary
from classnotes.models import Classnotes


def CardLink(title, url='#', number=None, ta_number=None):
  return namedtuple('CardLink', 'title url number ta_number')(title=title, url=url, number=number, ta_number=ta_number)


def Card(header_title, condition=True, card_links=[]):
  return namedtuple('Card', 'header_title condition card_links')(header_title=header_title, condition=condition, card_links=card_links)


register = template.Library()


# Generates all the cards
@register.assignment_tag(takes_context=True)
def generate_cards(context):
  user = context['user']
  if user.is_anonymous():
    return ""

  cards = []

  if user.has_group(['training_assistant']):

    # filter for trainees assigned to current TA and cross it with existing web requests
    my_trainees = Trainee.objects.filter(TA=user)

    web_access_count = WebRequest.objects.filter(status='P').count()
    web_access_ta_count = WebRequest.objects.filter(status='P', trainee__in=my_trainees).count()
    av_count = AudioRequest.objects.filter(status='P').count()
    av_ta_count = AudioRequest.objects.filter(status='P', trainee_author__in=my_trainees).count()

    my_trainees = User.objects.filter(TA=user)
    room_reservation_count = RoomReservation.objects.filter(status='P').count()

    announce_count = Announcement.objects.filter(status='P').count()

    TA_requests = Card(
        header_title="Requests",
        card_links=[
            CardLink(title="Web Access", url=reverse('web_access:web_access-list'), number=web_access_count, ta_number=web_access_ta_count),
            CardLink(title="AV", url=reverse('audio:ta-audio-home'), number=av_count, ta_number=av_ta_count),
            CardLink(title="Room Reservation", url=reverse('room_reservations:ta-room-reservation-list'),number=room_reservation_count),
            CardLink(title="Announcements", url=reverse('announcements:announcement-request-list'), number=announce_count)
        ]
    )

    cards.append(TA_requests)

    ls_p = IndividualSlip.objects.filter(status__in=['P', 'S'], TA=user).count() + GroupSlip.objects.filter(status__in=['P', 'S'], TA=user).count()
    ls_f = IndividualSlip.objects.filter(status='F', TA=user).count() + GroupSlip.objects.filter(status='F', TA=user).count()

    TA_leaveslips = Card(
        header_title="Leave Slips",
        card_links=[
            CardLink(title="Pending", url="%s?status=P&ta=%s" % (reverse('leaveslips:ta-leaveslip-list'), user.id), number=ls_p),
            CardLink(title="Marked for fellowship", url="%s?status=F&ta=%s" % (reverse('leaveslips:ta-leaveslip-list'), user.id), number=ls_f),
        ]
    )

    cards.append(TA_leaveslips)

    all_summ = Summary.objects.filter(approved=False)
    summ_count = 0
    for s in all_summ:
      if s.discipline and s.discipline.trainee in my_trainees:
        summ_count = summ_count + 1

    cn = Classnotes.objects.filter(status='P', trainee__in=my_trainees).count()

    TA_disciplines = Card(
        header_title="Discipline",
        card_links=[
            CardLink(title="Life Study Summaries", url=reverse('lifestudies:discipline_list'), number=summ_count),
            CardLink(title="Class Notes", url=reverse('classnotes:classnotes_list'), number=cn),
        ]
    )

    cards.append(TA_disciplines)

    TA_admin = Card(
        header_title="Administration",
        card_links=[
            CardLink(title="Exams", url=reverse('exams:manage')),
            CardLink(title="HC Forms", url=reverse('hc:hc-admin')),
            CardLink(title="Graduation", url=reverse('graduation:grad-admin')),
            CardLink(title="Trainee Information", url=reverse('trainee_information')),
            CardLink(title="Designated Services Viewer", url=reverse('services:designated_services_viewer')),
        ]
    )

    cards.append(TA_admin)

    TA_reports = Card(
        header_title="Reports",
        card_links=[
            CardLink(title="Life-Study", url=reverse('lifestudies:discipline_report')),
            CardLink(title="Class Notes", url=reverse('classnotes:classnotes_report')),
            CardLink(title="Bible Reading", url=reverse('bible_tracker:report')),
            CardLink(title="Service", url=reverse('services:services_schedule')),
        ]
    )

    cards.append(TA_reports)

  if user.has_group(['badges']):
    badge_card = Card(
        header_title='Badges',
        card_links=[
            CardLink(title="Badge Portal", url=reverse('badges:badges_list')),
        ]
    )
    cards.append(badge_card)

  if user.has_group(['service_schedulers']):
    service_card = Card(
        header_title='Service',
        card_links=[
            CardLink(title="Service Portal", url=reverse('services:services_view')),
            CardLink(title="Service Admin", url='admin/services/'),
            CardLink(title="Designated Services Viewer", url=reverse('services:designated_services_viewer')),
        ]
    )
    cards.append(service_card)

  if user.has_group(['attendance_monitors']):
    attendance_card = Card(
        header_title='Rolls',
        card_links=[
            CardLink(title="Class", url=reverse('attendance:class-rolls')),
            CardLink(title="House", url=reverse('attendance:house-rolls')),
            CardLink(title="Meal", url=reverse('attendance:meal-rolls')),
            CardLink(title="Study", url=reverse('attendance:study-rolls')),
            CardLink(title="Team", url=reverse('attendance:team-rolls')),
            CardLink(title="YPC", url=reverse('attendance:ypc-rolls')),
            CardLink(title="Assign trainees to schedules", url=reverse('schedules:assign-trainees')),
        ]
    )
    cards.append(attendance_card)

    schedules_card = Card(
        header_title='Admin',
        card_links=[
# Revoking the permissions just for the short term to stop AM's from changing schedules "benfin"
#           CardLink(title="Events", url='admin/schedules/event/'),
#           CardLink(title="Schedules", url='admin/schedules/schedule/'),
            CardLink(title="Roll", url='admin/attendance/roll/'),
        ]
    )
    cards.append(schedules_card)

  if user.has_group(['HC']):
    attendance_card = Card(
        header_title='House Coordinator',
        card_links=[
            CardLink(title="Daily attendance", url=reverse('absent_trainee_roster:absent_trainee_form')),
        ]
    )
    cards.append(attendance_card)

  return cards
