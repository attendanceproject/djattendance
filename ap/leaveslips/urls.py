from django.conf.urls import url

from leaveslips import views

urlpatterns = [
    url(r'individual/update/(?P<pk>\d+)$', views.IndividualSlipUpdate.as_view(), name='individual-update'),
    url(r'group/update/(?P<pk>\d+)$', views.GroupSlipUpdate.as_view(), name='group-update'),
    url(r'^$', views.LeaveSlipList.as_view(), name='leaveslips-list'),
    url(r'ta$', views.TALeaveSlipList.as_view(), name='ta-leaveslip-list'),
    url(r'(?P<classname>individual|group)/(?P<status>[APFDS])/(?P<id>\d+)$', views.modify_status, name='modify-status'),
    url(r'bulk/update/(?P<status>[APFDS])$', views.bulk_modify_status, name='bulk-modify-status')
]
