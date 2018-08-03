from django.conf.urls import url
from reports import views

urlpatterns = [
  url(r'^$', views.ReportCreateView.as_view(), name='generate-reports'),
  # url(r'report-generated/$', views.GeneratedReport.as_view(), name='report-generated'),
  # url(r'report-filtered/$', views.ReportFilterView.as_view(), name='report-filtered'),
  # url(r'report-filtered-generated/$', views.GeneratedFilteredReport.as_view(), name='report-filtered-generated'),
  url(r'generate_attendance_report/$', views.GenerateAttendanceReport.as_view(), name='generate-attendance-report'),
  url(r'attendance_report/$', views.AttendanceReport.as_view(), name='attendance-report'),
  url(r'attendance_report_trainee/$', views.attendance_report_trainee, name='attendance-report-individual-trainee'),
  url(r'attendance_report_zip/$', views.generate_zip, name='zip-attendance-report'),
]
