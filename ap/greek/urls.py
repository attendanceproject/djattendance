from django.conf.urls import url

from greek import views

urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^changeChapter/$', views.changeChapter, name='changeChapter'),
]