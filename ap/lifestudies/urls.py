from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^$', views.DisciplineListView.as_view(), name='discipline_list'),
  url(r'^discipline-report$', views.DisciplineReportView.as_view(), name='discipline_report'),
  url(r'^(?P<pk>\d+)/create-summary$', views.SummaryCreateView.as_view(), name='summary_create'),
  url(r'^(?P<pk>\d+)/detail-summary$', views.SummaryUpdateView.as_view(), name='summary_detail'),
  url(r'^(?P<pk>\d+)/approve-summary$', views.SummaryApproveView.as_view(), name='summary_approve'),
  url(r'^create-discipline$', views.DisciplineCreateView.as_view(), name='discipline_create'),
  url(r'^create-discipline-multiple$', views.multipleDisciplineCreateView, name='discipline_create_multiple'),
  url(r'^(?P<pk>\d+)/detail-discipline$', views.DisciplineDetailView.as_view(), name='discipline_detail'),
  url(r'^(?P<period>\d+)/attendance-assign$', views.AttendanceAssign.as_view(), name='attendance_assign'),
  url(r'^monday-report$', views.MondayReportView.as_view(), name='monday_report'),
]
