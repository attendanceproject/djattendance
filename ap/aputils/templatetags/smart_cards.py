from collections import namedtuple

from accounts.models import *
from announcements.models import Announcement
from audio.models import AudioRequest
from classnotes.models import Classnotes
from django import template
from django.core.urlresolvers import reverse
from house_requests.models import *
from leaveslips.models import GroupSlip, IndividualSlip
from lifestudies.models import Summary
from room_reservations.models import RoomReservation
from web_access.models import WebRequest


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

    web_access = WebRequest.objects.filter(status='P')
    web_access_count = web_access.count()
    web_access_ta_count = web_access.filter(trainee__in=my_trainees).count()

    av = AudioRequest.objects.filter(status='P')
    av_count = av.count()
    av_ta_count = av.filter(trainee_author__in=my_trainees).count()

    room_res = RoomReservation.objects.filter(status='P')
    room_reservation_count = room_res.count()
    room_reservations_ta_count = room_res.filter(requester__in=my_trainees).count()

    ann = Announcement.objects.filter(status='P')
    announce_count = ann.count()
    announce_ta_count = ann.filter(author__in=my_trainees).count()

    TA_requests = Card(
        header_title="Requests",
        card_links=[
            CardLink(title="Web Access", url=reverse('web_access:web_access-list'), number=web_access_count, ta_number=web_access_ta_count),
            CardLink(title="AV", url=reverse('audio:ta-audio-home'), number=av_count, ta_number=av_ta_count),
            CardLink(title="Room Reservation", url=reverse('room_reservations:ta-room-reservation-list'), number=room_reservation_count, ta_number=room_reservations_ta_count),
            CardLink(title="Announcements", url=reverse('announcements:announcement-request-list'), number=announce_count, ta_number=announce_ta_count)
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
    summ_count = all_summ.count()
    summ_ta_count = all_summ.filter(discipline__trainee__in=my_trainees).count()

    cn = Classnotes.objects.filter(status='P')
    cn_count = cn.count()
    cn_ta_count = cn.filter(trainee__in=my_trainees).count()

    TA_disciplines = Card(
        header_title="Discipline",
        card_links=[
            CardLink(title="Life Study Summaries", url=reverse('lifestudies:discipline_list'), number=summ_count, ta_number=summ_ta_count),
            CardLink(title="Class Notes", url=reverse('classnotes:classnotes_list'), number=cn_count, ta_number=cn_ta_count),
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
            CardLink(title="Designated Services Trainees", url=reverse('services:designated_services_viewer')),
            CardLink(title="Designated Services Hours", url=reverse('services:service_hours_ta_view')),
            CardLink(title="Interim Intentions", url=reverse('interim:interim_intentions_admin')),
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

  if user.has_group(['av']):
    audio_card = Card(
        header_title='A/V',
        card_links=[
            CardLink(title="Audio Files Admin", url='admin/audio/audiofile'),
        ]
    )
    cards.append(audio_card)

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
