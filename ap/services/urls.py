from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^$', views.services_view, name='services_view'),
  url(r'^assign$', views.services_view, {'run_assign': True}, name='services_assign_view'),
  url(r'^generate_leaveslips$', views.services_view, {'generate_leaveslips': True}, name='services_generate_leaveslips'),
  url(r'^add_exception/$', views.AddExceptionView.as_view(), name='services-exception-add'),
  url(r'^update_exception/(?P<pk>\d+)$', views.UpdateExceptionView.as_view(), name='services-exception-update'),
  url(r'^delete_exception/(?P<pk>\d+)$', views.UpdateExceptionView.as_view(), name='services-exception-delete'),
  url(r'^check_exceptions$', views.check_exceptions_view, name='services-exception-check'),
  url(r'^generate_schedule_house$', views.generate_report, {'house': True}, name='services_schedule_house'),
  url(r'^generate_schedule$', views.generate_report, name='services_schedule'),
  url(r'^generate_signinr$', views.generate_signin, {'r': True}, name='rservices_signin'),
  url(r'^generate_signink$', views.generate_signin, {'k': True}, name='kservices_signin'),
  url(r'^generate_signino$', views.generate_signin, {'o': True}, name='oservices_signin'),
  url(r'^import-guests$', views.ImportGuestsView.as_view(), name='import-guests'),
  url(r'^lock$', views.lock, name='lock-assignments'),
  url(r'^deactivate-guest/(?P<pk>\d+)$', views.deactivate_guest, name='deactivate-guest'),
  url(r'^deactivate-guest/bulk$', views.bulk_deactivate_guests, name="bulk-deactivate-guests"),
  url(r'^process-guests$', views.process_guests, name='process-guests'),
  url(r'^designated_service_hours/(?P<service_id>\d+)/(?P<week>\d+)', views.ServiceHours.as_view(), name='designated_service_hours'),
  url(r'^designated_service_hours$', views.ServiceHours.as_view(), name='designated_service_hours'),
  url(r'^service_hours_ta_view$', views.ServiceHoursTAView.as_view(), name='service_hours_ta_view'),
  url(r'^designated_services_viewer$', views.DesignatedServiceViewer.as_view(), name='designated_services_viewer'),
  url(r'^single_trainee_services_viewer$', views.SingleTraineeServicesViewer.as_view(), name='single_trainee_services_viewer'),
  url(r'^single_trainee_services_viewer/(?P<trainee_id>\d+)', views.SingleTraineeServicesViewer.as_view(), name='trainee_services_viewer'),
  url(r'^service_category_not_done_viewer$', views.ServiceCategoryNotDoneViewer.as_view(), name='service_category_not_done_viewer'),
  url(r'^service_category_not_done_viewer/(?P<category_id>\d+)', views.ServiceCategoryNotDoneViewer.as_view(), name='service_category_not_done_viewer_selected'),
  url(r'^service_category_counts_viewer$', views.ServiceCategoryCountsViewer.as_view(), name='service_category_counts_viewer'),
  url(r'^service_category_counts_viewer/(?P<category_id>\d+)', views.ServiceCategoryCountsViewer.as_view(), name='service_category_counts_viewer_selected'),
  url(r'^add_trainees_services/$', views.DesignatedServiceAdderViewer.as_view(), name='services_form')
]
