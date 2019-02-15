from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^faq/$', views.houseInspectionFaq, name='house_inspection_faq'),
    url(r'^manage_inspectors/$', views.manageInspectors, name='manage_inspectors'),
]


