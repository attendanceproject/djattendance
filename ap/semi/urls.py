from django.conf.urls import url
from semi import views

urlpatterns = [
  url(r'^attendance-report/$', views.AttendanceReport.as_view(), name='attendance-report'),
  url(r'^location-report/$', views.LocationReport.as_view(), name='location-report'),
  url(r'^personal-attendance/$', views.SemiView.as_view(), name='semi-base'),
  url(r'^(?P<status>[APFD])/(?P<id>\d+)$', views.modify_status, name='modify-status'),
  url(r'^location-request/(?P<pk>\d+)$', views.LocationUpdate.as_view(), name='location-request-detail'),
]
