from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^interim_intentions$', views.InterimIntentionsView.as_view(), name='interim_intentions'),
  url(r'^interim_intentions_admin$', views.InterimIntentionsAdminView.as_view(), name='interim_intentions_admin'),
  url(r'^ta_view$', views.InterimIntentionsTAView.as_view(), name='interim_intentions_ta_view'),
  url(r'^calendar_view$', views.InterimIntentionsCalendarView.as_view(), name='interim_intentions_calendar_view'),
]
