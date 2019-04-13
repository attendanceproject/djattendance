from django.conf.urls import url

from attendance import views
from attendance import more_views

urlpatterns = [
  url(r'^submit/$', views.AttendancePersonal.as_view(), name='attendance-submit'),
  url(r'^rolls/$', views.RollsView.as_view(), name='class-rolls'),
  url(r'^rolls/class/$', views.ClassRollsView.as_view(), name='class-table-rolls'),
  url(r'^rolls/meal/$', views.MealRollsView.as_view(), name='meal-rolls'),
  url(r'^rolls/study/$', views.StudyRollsView.as_view(), name='study-rolls'),
  url(r'^rolls/house/$', views.HouseRollsView.as_view(), name='house-rolls'),
  url(r'^rolls/team/$', views.TeamRollsView.as_view(), name='team-rolls'),
  url(r'^rolls/ypc/$', views.YPCRollsView.as_view(), name='ypc-rolls'),
  url(r'^rolls/rfid/$', views.RFIDRollsView.as_view(), name='rfid-rolls'),
  url(r'^rolls/finalize/$', views.finalize_rolls, name='finalize-rolls'),
  url(r'^api/rolls/finalize/$', views.finalize_personal, name='finalize'),
  url(r'^api/rolls/rfid/(?P<trainee_id>\d+)$', views.rfid_signin),
  url(r'^api/rolls/rfid-finalize/(?P<event_id>\d+)/(?P<event_date>\d{4}-\d{2}-\d{2})$', views.rfid_finalize, name='rfid-roll-finalize'),
  url(r'^api/rolls/rfid-tardy/(?P<event_id>\d+)/(?P<event_date>\d{4}-\d{2}-\d{2})$', views.rfid_tardy, name='rfid-roll-tardy'),
  url(r'^rolls/audit/$', views.AuditRollsView.as_view(), name='audit-rolls'),
  url(r'^rolls/json/$', more_views.RollsJSON.as_view(), name='rolls-json'),
  url(r'^rolls/viewer/$', more_views.RollsViewer.as_view(), name='rolls-viewer'),
  url(r'^personalslips/json/$', more_views.LeaveSlipsJSON.as_view(), name='leaveslips-json'),
  url(r'^personalslips/viewer/$', more_views.LeaveSlipViewer.as_view(), name='leaveslips-viewer'),
  url(r'^events/json/$', more_views.EventsJSON.as_view(), name='events-json'),
  url(r'^events/viewer/$', more_views.EventsViewer.as_view(), name='events-viewer'),
  url(r'^schedules/json/$', more_views.SchedulesJSON.as_view(), name='schedules-json'),
  url(r'^schedules/viewer/$', more_views.SchedulesViewer.as_view(), name='schedules-viewer'),
  url(r'^groupslips/json/$', more_views.GroupSlipsJSON.as_view(), name='groupslips-json'),
  url(r'^groupslips/viewer/$', more_views.GroupSlipViewer.as_view(), name='groupslips-viewer'),
  url(r'^admin/rolls/create/$', views.RollAdminCreate.as_view(), name='admin-roll-create'),
  url(r'^admin/rolls/(?P<pk>\d+)$', views.RollAdminUpdate.as_view(), name='admin-roll'),
  url(r'^admin/rolls/delete/(?P<pk>\d+)$', views.RollAdminDelete.as_view(), name='admin-roll-delete'),
  url(r'^admin/trainee-attendance/$', views.TraineeAttendanceAdminView.as_view(), name='admin-trainee-attendance'),
]
