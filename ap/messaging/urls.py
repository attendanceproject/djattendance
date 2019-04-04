from django.conf.urls import url

from messaging import views

urlpatterns = [
  url(r'^$', views.MessagingView.as_view(), name='messaging'),
]
