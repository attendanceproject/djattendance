from django.conf.urls import url

from web_access import views, utils
from web_access.models import WebRequest

urlpatterns = [
    url(r'^$', views.WebRequestList.as_view(), name='web_access-list'),
    url(r'^create$', views.WebAccessCreate.as_view(model=WebRequest), name='web_access-create'),
    url(r'^detail/(?P<pk>\d+)$', views.WebAccessDetail.as_view(), name='web_access-detail'),
    url(r'^update/(?P<pk>\d+)$', views.WebAccessUpdate.as_view(), name='web_access-update'),
    url(r'^delete/(?P<pk>\d+)$', views.WebAccessDelete.as_view(), name='web_access-delete'),
    url(r'^ta/update/(?P<pk>\d+)$', views.TAWebAccessUpdate.as_view(), name='web_access-update-ta'),
    url(r'^(?P<status>[APFDS])/(?P<id>\d+)$', views.modify_status, name='modify-status'),
    url(r'^start-access/(?P<id>\d+)$', utils.startAccess, name='start-access'),
    url(r'^eshepherding-access$', views.eShepherdingRequest, name='eshepherding-access'),
    url(r'^createGuestWebAccess$', views.createGuestWebAccess, name='create-guest-request'),
    url(r'^getGuestRequests$', views.getGuestRequests, name='get-guest-requests'),
    url(r'^direct-web-access$', views.directWebAccess, name='direct-web-access'),
    url(r'^get-remote-address$', utils.getRemoteAddress, name='get-remote-address'),
]
