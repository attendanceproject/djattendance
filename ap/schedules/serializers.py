import django_filters
from rest_framework.serializers import ModelSerializer
from .models import Event, Schedule
from rest_framework import serializers, filters
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)

from pytz import timezone
from tzlocal import get_localzone


local_tz = get_localzone()


class EventSerializer(BulkSerializerMixin, ModelSerializer):
  class Meta:
    model = Event
    list_serializer_class = BulkListSerializer
    ordering_fields = ('weekday', 'start')
    fields = '__all__'


class EventWithDateSerializer(BulkSerializerMixin, ModelSerializer):
  date = serializers.DateField(read_only=True)
  start_datetime = serializers.SerializerMethodField()
  end_datetime = serializers.SerializerMethodField()

  def get_start_datetime(self, obj):
    return localized_time_iso(obj.start_datetime)

  def get_end_datetime(self, obj):
    return localized_time_iso(obj.end_datetime)

  class Meta:
    model = Event
    list_serializer_class = BulkListSerializer
    fields = ['id', 'date', 'code', 'name', 'start_datetime', 'end_datetime']


def localized_time_iso(t):
  return timezone(str(local_tz)).localize(t).isoformat()


class AttendanceEventWithDateSerializer(BulkSerializerMixin, ModelSerializer):
  start_datetime = serializers.SerializerMethodField()
  end_datetime = serializers.SerializerMethodField()

  def get_start_datetime(self, obj):
    return localized_time_iso(obj.start_datetime)

  def get_end_datetime(self, obj):
    return localized_time_iso(obj.end_datetime)

  class Meta:
    model = Event
    list_serializer_class = BulkListSerializer
    fields = '__all__'


class EventFilter(filters.FilterSet):
  start__lt = django_filters.DateTimeFilter(name='start', lookup_expr='lt')
  start__gt = django_filters.DateTimeFilter(name='start', lookup_expr='gt')
  end__lt = django_filters.DateTimeFilter(name='end', lookup_expr='lt')
  end__gt = django_filters.DateTimeFilter(name='end', lookup_expr='gt')
  id__lt = django_filters.NumberFilter(name='id', lookup_expr='lt')
  id__gt = django_filters.NumberFilter(name='id', lookup_expr='gt')

  class Meta:
    model = Event
    fields = ['id', 'name', 'weekday', 'chart', 'monitor', 'type']


class ScheduleSerializer(BulkSerializerMixin, ModelSerializer):
  class Meta:
    model = Schedule
    list_serializer_class = BulkListSerializer
    fields = '__all__'


class ScheduleFilter(filters.FilterSet):
  class Meta:
    model = Schedule
    fields = ['id', 'trainees', 'weeks', 'events']
