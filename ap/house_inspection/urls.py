from django.conf.urls import url
from . import views
from .models import HouseInspectionFaq

urlpatterns = [
    url(r'^faq/$', views.houseInspectionFaq, name='house_inspection_faq'),
    url(r'^manage_scores/$', views.ManageScores.as_view(), name='manage_scores'),
    url(r'^manage_inspectors/$', views.manageInspectors, name='manage_inspectors'),
    url(r'^manage_inspectable_houses/$', views.manageInspectableHouses, name='manage_inspectable_houses'),
    url(r'^json/$', views.QuestionRequestJSON.as_view(), name='house_inspection_faq-json'),
    url(r'^question_list/$', views.QuestionList.as_view(), name='question_list'),
    url(r'^detail/(?P<pk>\d+)$', views.FaqDetail.as_view(), name='house_inspection_faq-detail'),
    url(r'^create$', views.FaqCreate.as_view(model=HouseInspectionFaq), name='faq-create'),
    url(r'^update/(?P<pk>\d+)$', views.FaqUpdate.as_view(), name='faq-update'),
    url(r'^delete/(?P<pk>\d+)$', views.FaqDelete.as_view(), name='faq-delete'),
    url(r'^answer/(?P<pk>\d+)$', views.InspectorAnswer.as_view(), name='inspector-answer'),
    url(r'^(?P<status>[APFDS])/(?P<id>\d+)$', views.modify_status, name='modify-status'),
    url(r'^ta/update/(?P<pk>\d+)$', views.FaqAnswer.as_view(), name='house_inspection-update-answer'),
    url(r'^ta/comment/(?P<pk>\d+)$', views.FaqTaComment.as_view(), name='house_inspection-faq-comment'),    
    #url(r'^iirjson/$', views.ItemizedInspectionReportJSON.as_view(), name='itemized_inspection_report-json'),
    url(r'^itemized_inspection_report/$', views.ItemizedInspectionReport.as_view(), name='itemized_inspection_report'),
]