from django.conf.urls import url

from schedules import views

app_name = 'schedules'

urlpatterns = [
    url(r'event/(?P<pk>\d+)/$', views.EventDetail.as_view(), name='event-detail'),
    url(r'event/(?P<pk>\d+)/delete/$', views.EventDelete.as_view(), name='event-delete'),
    url(r'event/(?P<term>(Fa|Sp)\d{2})/$', views.TermEvents.as_view(), name='term-events'),
    url(r'assign-trainees-to-schedule/(?P<pk>\d+)$', views.assign_trainees_view, name='assign-trainees'),
    url(r'assign-team-schedules/$', views.assign_team_schedules, name='assign-team-schedules'),
    url(r'clear-team-schedules/$', views.clear_team_schedules, name='clear-team-schedules'),
    url(r'clear-all-schedules/$', views.clear_all_schedules, name='clear-all-schedules'),
    url(r'^admin/events/create/$', views.EventAdminCreate.as_view(), name='admin-event-create'),
    url(r'^admin/events/(?P<pk>\d+)$', views.EventAdminUpdate.as_view(), name='admin-event'),
    url(r'^admin/events/delete/(?P<pk>\d+)$', views.EventAdminDelete.as_view(), name='admin-event-delete'),
    url(r'^admin/schedules/table/$', views.AllSchedulesView.as_view(), name='admin-schedule-table'),
    url(r'^admin/schedules/create/$', views.ScheduleAdminCreate.as_view(), name='admin-schedule-create'),
    url(r'^admin/schedules/(?P<pk>\d+)$', views.ScheduleAdminUpdate.as_view(), name='admin-schedule'),
    url(r'^admin/schedules/split/(?P<pk>\d+)/(?P<week>\d+)$', views.split_schedules_view, name='admin-schedule-split'),
    url(r'^afternoon_changes', views.AfternoonClassChange.as_view(), name='afternoon-class-change'),
    url(r'^admin/schedules/delete-rolls/$', views.scheduleCRUD_delete_rolls, name='delete-conflicting-rolls'),
]
