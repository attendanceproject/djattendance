from django.conf.urls import url

from house_requests import views

app_name = 'house_requests'

urlpatterns = [
  url(r'^maintenance_list/$', views.MaintenanceRequestList.as_view(), name='maintenance-list'),
  url(r'^maintenance_json/$', views.MaintenanceRequestJSON.as_view(), name='maintenance-json'),
  url(r'^maintenance_request/$', views.MaintenanceRequestCreate.as_view(), name='maintenance-request'),
  url(r'^maintenance_update/(?P<pk>\d+)$', views.MaintenanceRequestUpdate.as_view(), name='maintenance-update'),
  url(r'^maintenance_detail/(?P<pk>\d+)$', views.MaintenanceRequestDetail.as_view(), name='maintenance-detail'),
  url(r'^maintenance_delete/(?P<pk>\d+)$', views.MaintenanceRequestDelete.as_view(), name='maintenance-delete'),
  url(r'^maintenance_modify/(?P<status>[CPF])/(?P<id>\d+)$', views.modify_maintenance_status, name='maintenance-modify-status'),
  url(r'^maintenance_tacomment/(?P<pk>\d+)$', views.MaintenanceRequestTAComment.as_view(), name='maintenance-tacomment'),
  url(r'^maintenance_report/$', views.MaintenanceReport, name='maintenance-report'),

  url(r'^linens_list/$', views.LinensRequestList.as_view(), name='linens-list'),
  url(r'^linens_json/$', views.LinensRequestJSON.as_view(), name='linens-json'),
  url(r'^linens_request/$', views.LinensRequestCreate.as_view(), name='linens-request'),
  url(r'^linens_update/(?P<pk>\d+)$', views.LinensRequestUpdate.as_view(), name='linens-update'),
  url(r'^linens_detail/(?P<pk>\d+)$', views.LinensRequestDetail.as_view(), name='linens-detail'),
  url(r'^linens_delete/(?P<pk>\d+)$', views.LinensRequestDelete.as_view(), name='linens-delete'),
  url(r'^linens_modify/(?P<status>[CPF])/(?P<id>\d+)$', views.modify_linens_status, name='linens-modify-status'),
  url(r'^linens_tacomment/(?P<pk>\d+)$', views.LinensRequestTAComment.as_view(), name='linens-tacomment'),

  url(r'^framing_list/$', views.FramingRequestList.as_view(), name='framing-list'),
  url(r'^framing_json/$', views.FramingRequestJSON.as_view(), name='framing-json'),
  url(r'^framing_request/$', views.FramingRequestCreate.as_view(), name='framing-request'),
  url(r'^framing_update/(?P<pk>\d+)$', views.FramingRequestUpdate.as_view(), name='framing-update'),
  url(r'^framing_detail/(?P<pk>\d+)$', views.FramingRequestDetail.as_view(), name='framing-detail'),
  url(r'^framing_delete/(?P<pk>\d+)$', views.FramingRequestDelete.as_view(), name='framing-delete'),
  url(r'^framing_modify/(?P<status>[CPF])/(?P<id>\d+)$', views.modify_framing_status, name='framing-modify-status'),
  url(r'^framing_tacomment/(?P<pk>\d+)$', views.FramingRequestTAComment.as_view(), name='framing-tacomment'),

  url(r'^house_requests/$', views.NewRequestPage, name='house-requests'),
]
