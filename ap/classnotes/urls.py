from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^$', views.ClassnotesListView.as_view(), name='classnotes_list'),
  url(r'^classnotes-assign$', views.ClassnotesAssignView.as_view(), name='classnotes_assign'),
  url(r'^classnotes-create$', views.ClassnotesCreateView.as_view(), name='classnotes_create'),
  url(r'^classnotes-report$', views.ClassnotesReportView.as_view(), name='classnotes_report'),
  url(r'^classnotes-single-trainee$', views.ClassnotesSingleTraineeView.as_view(), name='classnotes_single_trainee'),
  url(r'^(?P<pk>\d+)/detail-classnotes$', views.ClassnotesUpdateView.as_view(), name='classnotes_detail'),
  url(r'^(?P<pk>\d+)/approve-classnotes$', views.ClassnotesApproveView.as_view(), name='classnotes_approve'),
]
