from django.conf.urls import url
from reports import views

urlpatterns = [
  url(r'attendance_report_generate/$', views.GenerateAttendanceReport.as_view(), name='generate-attendance-report'),
  url(r'attendance_report/$', views.AttendanceReport.as_view(), name='attendance-report'),
  url(r'attendance_report_trainee/$', views.attendance_report_trainee, name='attendance-report-individual-trainee'),
  url(r'attendance_report_zip/$', views.generate_zip, name='zip-attendance-report'),
]
