from django.conf.urls import url
from gospel_trips import views

urlpatterns = [
  url(r'^admin/$', views.GospelTripView.as_view(), name='admin-create'),
  url(r'^admin/(?P<pk>\d+)$', views.gospel_trip_admin_update, name='admin-update'),
  url(r'^admin/(?P<pk>\d+)/delete$', views.gospel_trip_admin_delete, name='admin-delete'),
  url(r'^admin/(?P<pk>\d+)/duplicate$', views.gospel_trip_admin_duplicate, name='admin-duplicate'),
  url(r'^admin/(?P<pk>\d+)/(?P<trainee>\d+)$', views.clear_application, name='admin-clear-app'),
  url(r'^admin/(?P<pk>\d+)/destinations/$', views.DestinationEditorView.as_view(), name='destination-editor'),
  url(r'^admin/(?P<pk>\d+)/destinations/add$', views.destination_add, name='destination-add'),
  url(r'^admin/(?P<pk>\d+)/destinations/remove$', views.destination_remove, name='destination-remove'),
  url(r'^admin/(?P<pk>\d+)/destinations/edit$', views.destination_edit, name='destination-edit'),
  url(r'^admin/(?P<pk>\d+)/destinations/trainee-role$', views.assign_trainee_role, name='assign-trainee-role'),
  url(r'^admin/(?P<pk>\d+)/destinations/assign-destination$', views.assign_destination, name='assign-destination'),
  url(r'^admin/(?P<pk>\d+)/by-preference/$', views.DestinationByPreferenceView.as_view(), name='by-preference'),
  url(r'^admin/(?P<pk>\d+)/by-group/$', views.DestinationByGroupView.as_view(), name='by-group'),
  url(r'^admin/(?P<pk>\d+)/rosters-individual/$', views.RostersIndividualTeamView.as_view(), name='rosters-individual'),
  url(r'^admin/(?P<pk>\d+)/nontrainee-report/$', views.NonTraineeReportView.as_view(), name='nontrainee-report'),
  url(r'^rosters/$', views.rosters_base, name='rosters-base'),
  url(r'^rosters/(?P<pk>\d+)/$', views.RostersAllTeamsView.as_view(), name='rosters-all'),
  url(r'^report/(?P<pk>\d+)$', views.GospelTripReportView.as_view(), name='report'),
  url(r'^trip/$', views.gospel_trip_base, name='trip-base'),
  url(r'^trip/(?P<pk>\d+)$', views.gospel_trip_trainee, name='gospel-trip'),
  url(r'^trip/(?P<pk>\d+)/nontrainee$', views.NonTraineeView.as_view(), name='nontrainee'),
  url(r'^trip/(?P<pk>\d+)/nontrainee/(?P<ntpk>\d+)$', views.NonTraineeView.as_view(), name='nontrainee-update'),
  url(r'^upload/$', views.upload_image, name='upload-image'),
]
