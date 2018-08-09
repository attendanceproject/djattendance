from django.conf.urls import url
from reports import views

urlpatterns = [
  url(r'generate-attendance-report/$', views.GenerateAttendanceReport.as_view(), name='generate-attendance-report'),
  url(r'attendance-report/$', views.AttendanceReport.as_view(), name='attendance-report'),
  url(r'attendance-report-trainee/$', views.attendance_report_trainee, name='attendance-report-individual-trainee'),
  url(r'attendance-report-zip/$', views.generate_zip, name='zip-attendance-report'),
  url(r'attendance-report-csv/$', views.generate_csv, name='csv-attendance-report'),
]
