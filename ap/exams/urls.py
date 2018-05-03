from django.conf.urls import url
from exams import views

urlpatterns = [
    url(r'^$', views.ExamTemplateListView.as_view(), name='list'),
    url(r'taken/$', views.ExamTemplateListView.as_view(), {'taken': True}, name='taken'),
    url(r'manage/$', views.ExamTemplateListView.as_view(), {'manage': True}, name='manage'),
    url(r'new/$', views.ExamCreateView.as_view(), name='new'),
    url(r'manage/delete/(?P<pk>\d+)$', views.ExamDelete.as_view(), name='delete'),
    url(r'^(?P<pk>\d+)/edit$', views.ExamEditView.as_view(), name='edit'),
    url(r'^(?P<pk>\d+)/preview$', views.PreviewExamView.as_view(), name='preview'),
    url(r'^(?P<pk>\d+)/take$', views.TakeExamView.as_view(), name='take'),
    url(r'^(?P<pk>\d+)/grade$', views.GradeExamView.as_view(), name='grade'),
    url(r'^(?P<pk>\d+)/graded$', views.GradedExamView.as_view(), name='graded'),
    url(r'^(?P<pk>\d+)/grades$', views.SingleExamGradesListView.as_view(), name='grades'),
    url(r'^(?P<pk>\d+)/overview$', views.GenerateOverview.as_view(), name='overview'),
    url(r'^makeup$', views.ExamMakeupView.as_view(), name='makeups'),
    url(r'^makeup/(?P<pk>\d+)$', views.ExamMakeupView.as_view(), name='makeup'),
    url(r'report/$', views.GenerateGradeReports.as_view(), name='report-all')
]
