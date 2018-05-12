from django.conf.urls import url

from leaveslips import views

urlpatterns = [
    url(r'individual/update/(?P<pk>\d+)$', views.IndividualSlipUpdate.as_view(), name='individual-update'),
    url(r'group/update/(?P<pk>\d+)$', views.GroupSlipUpdate.as_view(), name='group-update'),
    url(r'^$', views.LeaveSlipList.as_view(), name='leaveslips-list'),
    url(r'ta$', views.TALeaveSlipList.as_view(), name='ta-leaveslip-list'),
    url(r'(?P<classname>individual|group)/(?P<status>[APFDS])/(?P<id>\d+)$', views.modify_status, name='modify-status'),
    url(r'bulk/update/(?P<status>[APFDS])$', views.bulk_modify_status, name='bulk-modify-status'),
    url(r'^admin/leaveslips/create/$', views.IndividualSlipAdminCreate.as_view(), name='admin-islip-create'),
    url(r'^admin/leaveslips/(?P<pk>\d+)$', views.IndividualSlipAdminUpdate.as_view(), name='admin-islip'),
    url(r'^admin/leaveslips/delete/(?P<pk>\d+)$', views.IndividualSlipAdminDelete.as_view(), name='admin-islip-delete'),
    url(r'^admin/groupslips/create/$', views.GroupSlipAdminCreate.as_view(), name='admin-gslip-create'),
    url(r'^admin/groupslips/(?P<pk>\d+)$', views.GroupSlipAdminUpdate.as_view(), name='admin-gslip'),
    url(r'^admin/groupslips/delete/(?P<pk>\d+)$', views.GroupSlipAdminDelete.as_view(), name='admin-gslip-delete')
]
