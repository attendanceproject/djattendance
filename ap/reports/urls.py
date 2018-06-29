from django.conf.urls import url
from reports import views

urlpatterns = [
  url(r'^$', views.ReportCreateView.as_view(), name='generate-reports'),
  url(r'report-generated/$', views.GeneratedReport.as_view(), name='report-generated'),
  url(r'report-filtered/$', views.ReportFilterView.as_view(), name='report-filtered'),
  url(r'report-filtered-generated/$', views.GeneratedFilteredReport.as_view(), name='report-filtered-generated')
]