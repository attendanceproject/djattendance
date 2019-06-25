from django.conf.urls import url

from room_reservations import views

app_name = 'room_reservations'

urlpatterns = [
    url(r'ta$', views.TARoomReservationList.as_view(), name='ta-room-reservation-list'),
    url(r'update/(?P<pk>\d+)$', views.RoomReservationUpdate.as_view(), name='room-reservation-update'),
    url(r'submit/$', views.RoomReservationSubmit.as_view(), name='room-reservation-submit'),
    url(r'(?P<status>[ADF])/(?P<id>\d+)$', views.reservation_modify_status, name='reservation-modify-status'),
    url(r'schedule$', views.RoomReservationSchedule.as_view(), name='room-reservation-schedule'),
    url(r'^delete/(?P<pk>\d+)$', views.RoomReservationDelete.as_view(), name='room-reservation-delete'),
    url(r'^delete/$', views.RoomReservationDelete.as_view(), name='room-reservation-delete-base'),
    url(r'^tv_page$', views.RoomReservationTVView.as_view(), name='room-reservation-tv-page'),
    url(r'^itero_page$', views.RoomReservationIteroView.as_view(), name='room-reservation-itero-page'),
    url(r'^weather$', views.weather_api, name='weather'),
    url(r'^tv_page_version$', views.tv_page_version, name='tv-page-version'),
    url(r'^tv_page_reservations$', views.tv_page_reservations, name='tv-page-reservations'),
    url(r'^tv_page_ticker$', views.tv_page_ticker, name='tv-page-ticker'),
]
