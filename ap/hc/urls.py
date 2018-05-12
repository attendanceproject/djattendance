from django.conf.urls import url
from hc import views

app_name = 'hc'

urlpatterns = [
  url(r'hc_admin/$', views.HCSurveyAdminCreate.as_view(), name='hc-admin'),
  url(r'hc_admin_update/(?P<pk>\d+)$', views.HCSurveyAdminUpdate.as_view(), name='hc-admin-update'),
  url(r'hc_admin_delete/(?P<pk>\d+)$', views.HCSurveyAdminDelete.as_view(), name='hc-admin-delete'),
  url(r'hc_survey/$', views.submit_hc_survey, name='hc-survey'),
  url(r'hc_recommendation/$', views.HCRecommendationCreate.as_view(), name='hc-recommendation'),
  url(r'hc_recommendation/update/(?P<pk>\d+)$', views.HCRecommendationUpdate.as_view(), name='hc-recommendation-update'),
  url(r'hc_survey_ta_view/(?P<index>\d+)$', views.HCSurveyTAView.as_view(), name='hc-survey-ta-view'),
  url(r'hc_recommendation_ta_view/', views.HCRecommendationTAView.as_view(), name='hc-recommendation-ta-view'),
]
