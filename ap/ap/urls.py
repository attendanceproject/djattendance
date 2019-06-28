# coding: utf-8
import django
from accounts.views import *
from attendance.views import (AllAttendanceViewSet, AllRollViewSet,
                              AttendanceViewSet, RollViewSet)
from audio.views import AudioRequestViewSet
from books.views import BooksViewSet
from classnotes.views import ClassNoteViewSet
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import login as auth_login
from django.contrib.auth.views import logout_then_login
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django_nyt.urls import get_pattern as get_nyt_pattern
from leaveslips.views import (AllGroupSlipViewSet, AllIndividualSlipViewSet,
                              GroupSlipViewSet, IndividualSlipViewSet)
from lifestudies.views import DisciplineSummariesViewSet
from meal_seating.views import TableViewSet
from rest_framework_bulk.routes import BulkRouter
from rest_framework_nested import routers
from rest_framework_swagger.views import get_swagger_view
from schedules.views import (AllEventViewSet, AllScheduleViewSet, EventViewSet,
                             ScheduleViewSet)
from seating.views import ChartViewSet, PartialViewSet, SeatViewSet
from services.views import (AssignmentPinViewSet, AssignmentViewSet,
                            ExceptionActiveViewSet, ServiceActiveViewSet,
                            ServiceSlotWorkloadViewSet, ServiceTimeViewSet,
                            UpdateWorkersViewSet)
from terms.views import TermViewSet
from web_access.forms import WebAccessRequestGuestCreateForm as form
from wiki.urls import get_pattern as get_wiki_pattern

from .views import (custom404errorview, custom500errorview, custom502errorview,
                    custom503errorview, custom504errorview, home)
from . import views

admin.autodiscover()

urlpatterns = [
  url(r'^$', home, name='home'),
  url(r'^accounts/login/$', auth_login, {'extra_context': {'webaccess_form': form}}, name='login'),
  url(r'^accounts/logout/$', logout_then_login, name='logout'),
  url(r'^accounts/', include('accounts.urls')),
  url(r'^audio/', include('audio.urls', namespace='audio')),
  url(r'^dailybread/', include('dailybread.urls', namespace="dailybread")),
  url(r'^badges/', include('badges.urls', namespace="badges")),
  url(r'^schedules/', include('schedules.urls', namespace="schedules")),
  url(r'^attendance/', include('attendance.urls', namespace="attendance")),
  url(r'^leaveslips/', include('leaveslips.urls', namespace="leaveslips")),
  url(r'^verse_parse/', include('verse_parse.urls', namespace="verse_parse")),
  url(r'^meal_seating/', include('meal_seating.urls')),
  url(r'^absent_trainee_roster/', include('absent_trainee_roster.urls', namespace="absent_trainee_roster")),
  url(r'^syllabus/', include('syllabus.urls', namespace="syllabus")),
  url(r'^classnotes/', include('classnotes.urls', namespace="classnotes")),
  url(r'^classes/', include('classes.urls', namespace="classes")),
  url(r'^lifestudies/', include('lifestudies.urls', namespace="lifestudies")),
  url(r'^seating/', include('seating.urls', namespace='seating')),
  url(r'^exams/', include('exams.urls', namespace="exams")),
  url(r'^web_access/', include('web_access.urls', namespace="web_access")),
  url(r'^apimport/', include('apimport.urls', namespace="apimport")),
  url(r'^bible_tracker/', include('bible_tracker.urls', namespace='bible_tracker')),
  url(r'^announcements/', include('announcements.urls', namespace='announcements')),
  url(r'^reports/', include('reports.urls', namespace='reports')),
  url(r'^services/', include('services.urls', namespace="services")),
  url(r'^semi/', include('semi.urls', namespace="semi")),
  url(r'^house_requests/', include('house_requests.urls', namespace="house_requests")),
  url(r'^hc/', include('hc.urls', namespace="hc")),
  url(r'^room_reservations/', include('room_reservations.urls', namespace="room_reservations")),
  url(r'^gospel_trips/', include('gospel_trips.urls', namespace="gospel_trips")),
  url(r'^graduation/', include('graduation.urls', namespace="graduation")),
  url(r'^xb/', include('xb_application.urls', namespace="xb")),
  url(r'^interim/', include('interim.urls', namespace="interim")),
  url(r'^gospel_statistics/', include('gospel_statistics.urls', namespace="gospel_statistics")),
  url(r'^house_inspection/', include('house_inspection.urls', namespace='house_inspection')),
  # admin urls
  url(r'^adminactions/', include('adminactions.urls')),  # django-adminactions pluggable app
  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  url(r'^admin/', include(admin.site.urls)),
  url(r'^admin/', include("massadmin.urls")),
  url(r'^static/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.STATIC_ROOT}),
  # fobi urls
  # DB Store plugin URLs
  url(r'^fobi/plugins/form-handlers/db-store/', include('fobi.contrib.plugins.form_handlers.db_store.urls')),
  url(r'^fobi/plugins/form-wizard-handlers/db-store/', include('fobi.contrib.plugins.form_handlers.db_store.urls.form_wizard_handlers')),
  # View URLs
  url(r'^forms/', include('fobi.urls.view')),
  # Edit URLs
  url(r'^forms/', include('fobi.urls.edit')),
  url(r'^404/$', custom404errorview),  # for development
  url(r'^500/$', custom500errorview),  # for development
  url(r'^502/$', custom502errorview),  # for development
  url(r'^503/$', custom503errorview),  # for development
  url(r'^504/$', custom504errorview),  # for development
  url(r'^printer/$', views.printerinstructions),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

router = BulkRouter()
router.register(r'users', UserViewSet)
router.register(r'trainees', TraineeViewSet, base_name='trainees')
router.register(r'events', EventViewSet)
router.register(r'allevents', AllEventViewSet, base_name='allevents')
router.register(r'schedules', ScheduleViewSet)
router.register(r'allschedules', AllScheduleViewSet, base_name='allschedules')
router.register(r'rolls', RollViewSet)
router.register(r'allrolls', AllRollViewSet, base_name='allrolls')
router.register(r'individualslips', IndividualSlipViewSet)
router.register(r'allindividualleaveslips', AllIndividualSlipViewSet, base_name='allindividualslips')
router.register(r'groupslips', GroupSlipViewSet)
router.register(r'allgroupslips', AllGroupSlipViewSet, base_name='allgroupslips')
router.register(r'books', BooksViewSet)
router.register(r'summaries', DisciplineSummariesViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'allattendance', AllAttendanceViewSet, base_name='allattendance')
router.register(r'audio', AudioRequestViewSet)
router.register(r'charts', ChartViewSet)
router.register(r'seats', SeatViewSet)
router.register(r'partials', PartialViewSet)
router.register(r'terms', TermViewSet)
router.register(r'classnotes', ClassNoteViewSet)
router.register(r'update-workers', UpdateWorkersViewSet, base_name='updateworkers')
router.register(r'update-workloads', ServiceSlotWorkloadViewSet, base_name='updateworkload')
router.register(r'update-active-services', ServiceActiveViewSet, base_name='updateservice')
router.register(r'update-time-services', ServiceTimeViewSet, base_name='updatetime')
router.register(r'update-exception-active', ExceptionActiveViewSet)
router.register(r'service-assignments', AssignmentViewSet, base_name='serviceassignments')
router.register(r'service-assignments-pin', AssignmentPinViewSet)
router.register(r'tables', TableViewSet)

attendance_router = routers.NestedSimpleRouter(router, r'attendance', lookup='attendance')
attendance_router.register(r'rolls', RollViewSet, base_name='rolls')
rolls_router = routers.NestedSimpleRouter(attendance_router, r'rolls', lookup='rolls')
attendance_router.register(r'events', EventViewSet, base_name='events')
events_router = routers.NestedSimpleRouter(attendance_router, r'events', lookup='events')
attendance_router.register(r'schedules', ScheduleViewSet, base_name='schedules')
schedules_router = routers.NestedSimpleRouter(attendance_router, r'schedules', lookup='schedules')
attendance_router.register(r'individualslips', IndividualSlipViewSet, base_name='individualslips')
leaveslips_router = routers.NestedSimpleRouter(attendance_router, r'individualslips', lookup='individualslips')
attendance_router.register(r'groupslips', GroupSlipViewSet, base_name='groupslips')
groupleaveslips_router = routers.NestedSimpleRouter(attendance_router, r'groupslips', lookup='groupslips')

urlpatterns += [
  url(r'^api/trainees/gender/(?P<gender>[BS])/$', TraineesByGender.as_view()),
  url(r'^api/trainees/term/(?P<term>[1234])/$', TraineesByTerm.as_view()),
  url(r'^api/trainees/team/(?P<pk>\d+)/$', TraineesByTeam.as_view()),
  url(r'^api/trainees/teamtype/(?P<type>\w+)/$', TraineesByTeamType.as_view()),
  url(r'^api/trainees/house/(?P<pk>\d+)/$', TraineesByHouse.as_view()),
  url(r'^api/trainees/locality/(?P<pk>\d+)/$', TraineesByLocality.as_view()),
  url(r'^api/trainees/hc/$', TraineesHouseCoordinators.as_view()),
  url(r'^api/', include(router.urls, namespace='rest_framework')),
  url(r'^api/', include(attendance_router.urls)),
  # third party
  url(r'^docs/', get_swagger_view(title='DJAttendance API documentation')),
  url(r'^explorer/', include('explorer.urls')),
  url(r'^select2/', include('django_select2.urls')),
]

urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
  import debug_toolbar
  urlpatterns += [
    url(r'^__debug__/', include(debug_toolbar.urls)),
  ]

urlpatterns += [
  url(r'^notifications/', get_nyt_pattern()),
  url(r'wiki', get_wiki_pattern())
]

handler404 = 'ap.views.custom404errorview'  # if settings.DEBUG = FALSE
handler500 = 'ap.views.custom500errorview'  # if settings.DEBUG = FALSE
handler500 = 'ap.views.custom502errorview'  # if settings.DEBUG = FALSE
handler503 = 'ap.views.custom503errorview'  # if settings.DEBUG = FALSE
handler500 = 'ap.views.custom504errorview'  # if settings.DEBUG = FALSE
