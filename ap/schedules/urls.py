from django.conf.urls import url

from schedules import views

urlpatterns = [
    url(r'event/(?P<pk>\d+)/$', views.EventDetail.as_view(), name='event-detail'),
    url(r'event/(?P<pk>\d+)/delete/$', views.EventDelete.as_view(), name='event-delete'),
    url(r'event/(?P<term>(Fa|Sp)\d{2})/$', views.TermEvents.as_view(), name='term-events'),
    url(r'assign_schedules_to_trainees/$', views.assign_trainees_to_schedules, name='assign-trainees'),
    url(r'^admin/events/create/$', views.EventAdminCreate.as_view(), name='admin-event-create'),
    url(r'^admin/events/(?P<pk>\d+)$', views.EventAdminUpdate.as_view(), name='admin-event'),
    url(r'^admin/events/delete/(?P<pk>\d+)$', views.EventAdminDelete.as_view(), name='admin-event-delete'),
    url(r'^admin/schedules/create/$', views.ScheduleAdminCreate.as_view(), name='admin-schedule-create'),
    url(r'^admin/schedules/(?P<pk>\d+)$', views.ScheduleAdminUpdate.as_view(), name='admin-schedule'),
    url(r'^admin/schedules/delete/(?P<pk>\d+)$', views.ScheduleAdminDelete.as_view(), name='admin-schedule-delete'),
    url(r'^admin/schedules/split/(?P<pk>\d+)/(?P<week>\d+)$', views.split_schedules_view, name='admin-schedule-split')
]
