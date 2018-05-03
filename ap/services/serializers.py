from .models import Worker, ServiceSlot, Service, Assignment, ServiceException
from rest_framework import serializers
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)

from rest_framework.serializers import ModelSerializer


class UpdateWorkerSerializer(BulkSerializerMixin, ModelSerializer):
  class Meta(object):
    model = Worker
    list_serializer_class = BulkListSerializer
    fields = ['id', 'health', 'services_cap']


class ServiceSlotWorkloadSerializer(BulkSerializerMixin, ModelSerializer):
  class Meta(object):
    model = ServiceSlot
    list_serializer_class = BulkListSerializer
    fields = ['id', 'workers_required']


class ServiceActiveSerializer(BulkSerializerMixin, ModelSerializer):
  class Meta(object):
    model = Service
    list_serializer_class = BulkListSerializer
    fields = ['id', 'active']


class ServiceTimeSerializer(BulkSerializerMixin, ModelSerializer):
  class Meta(object):
    model = Service
    list_serializer_class = BulkListSerializer
    fields = ['id', 'name', 'weekday', 'start', 'end']


class ExceptionActiveSerializer(BulkSerializerMixin, ModelSerializer):
  class Meta(object):
    model = ServiceException
    list_serializer_class = BulkListSerializer
    fields = ['id', 'active']


class WorkerIDSerializer(BulkSerializerMixin, ModelSerializer):
  # fullname = serializers.CharField(read_only=True)
  class Meta(object):
    model = Worker
    list_serializer_class = BulkListSerializer
    fields = ['id', 'full_name']


class WorkerAssignmentSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta(object):
        model = Assignment
        list_serializer_class = BulkListSerializer
        fields = ['id', 'workers', 'service_slot', 'service', 'week_schedule']


class AssignmentPinSerializer(BulkSerializerMixin, ModelSerializer):
  class Meta(object):
    model = Assignment
    list_serializer_class = BulkListSerializer
    fields = ['id', 'pin']


class ServiceCalendarSerializer(BulkSerializerMixin, ModelSerializer):
  start = serializers.DateTimeField(source='startdatetime', read_only=True)
  end = serializers.DateTimeField(source='enddatetime', read_only=True)
  title = serializers.CharField(source='name')

  class Meta(object):
    model = Service
    list_serializer_class = BulkListSerializer
    fields = ['id', 'title', 'category', 'designated', 'worker_groups', 'start', 'end']
