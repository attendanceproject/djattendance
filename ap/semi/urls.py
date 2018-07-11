from django.conf.urls import url
from semi import views

urlpatterns = [
  url(r'^attendance/$', views.AttendanceUpdate.as_view(), name='attendance-base'),
  url(r'^attendance/(?P<pk>\d+)$', views.AttendanceUpdate.as_view(), name='attendance'),
  url(r'^attendance-report/$', views.AttendanceReport.as_view(), name='attendance-report'),
  url(r'^location/$', views.LocationUpdate.as_view(), name='location-base'),
  url(r'^location/(?P<pk>\d+)$', views.LocationUpdate.as_view(), name='location'),
  url(r'^location-report/$', views.LocationReport.as_view(), name='location-report'),
]
