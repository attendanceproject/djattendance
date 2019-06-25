from django.conf.urls import url

from gospel_statistics import views

urlpatterns = [
  # Trainee side
  url(r'^$', views.GospelStatisticsView.as_view(), name='gospel-statistics-view'),
  url(r'^(?P<week>\d+)/$', views.GospelStatisticsView.as_view(), name='gospel-statistics-view'),
  url(r'^new-pair/$', views.NewGospelPairView.as_view(), name='new-pair'),
  url(r'^delete$', views.delete_pair, name='delete-pair'),
  # TA side
  url(r'^ta$', views.TAGospelStatisticsView, name='ta-gospel-statistics-view'),
  url(r'^generate-report/$', views.GenerateReportView.as_view(), name='generate-report'),
]
