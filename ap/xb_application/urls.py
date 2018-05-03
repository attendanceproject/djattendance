from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'xb_application$', views.XBApplicationView.as_view(), name='xb-application'),
    url(r'xb_report$', views.XBReportView.as_view(), name='xb-report'),
    url(r'xb_app/(?P<pk>\d+)$', views.XBApplicationDetails.as_view(), name='xb-application-view'),
]
