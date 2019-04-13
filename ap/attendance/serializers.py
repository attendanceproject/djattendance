from datetime import *

import django_filters
from accounts.models import Trainee
from leaveslips.models import IndividualSlip
from leaveslips.serializers import (GroupSlipSerializer,
                                    IndividualSlipSerializer)
from rest_framework import filters
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_bulk import BulkListSerializer, BulkSerializerMixin

from .models import Roll, RollsFinalization


class RollSerializer(BulkSerializerMixin, ModelSerializer):

  class Meta(object):
    model = Roll
    list_serializer_class = BulkListSerializer
    fields = ['id', 'event', 'trainee', 'status', 'finalized', 'notes', 'last_modified', 'submitted_by', 'date']
    validators = [UniqueTogetherValidator(
        queryset=Roll.objects.all(),
        fields=('trainee', 'event', 'date', 'submitted_by', 'status'),
        message='Duplication error for key fields, same status')]

  def create(self, validated_data):
    trainee = validated_data['trainee']
    event = validated_data['event']
    date = validated_data['date']
    status = validated_data['status']

    # checks if roll exists for given trainee, event, and date
    roll_override = Roll.objects.filter(trainee=trainee, event=event.id, date=date)

    if roll_override.count() == 0:
      if status == 'P':  # Don't create a present roll.
        return validated_data
      else:  # if no pre-existing rolls, create.
        return Roll.objects.create(**validated_data)
    else:
      roll = roll_override.first()
      leaveslips = IndividualSlip.objects.filter(rolls=roll)
      if status == 'P' and not leaveslips.exists():  # if input roll is "P" and no leave slip, delete it
        roll.delete()
        return validated_data
      roll.status = status
      roll.submitted_by = roll.trainee
      roll.last_modified = datetime.now()
      roll.save()
      return validated_data


class RollFilter(filters.FilterSet):
  timestamp__lt = django_filters.DateTimeFilter(name='timestamp', lookup_expr='lt')
  timestamp__gt = django_filters.DateTimeFilter(name='timestamp', lookup_expr='gt')
  finalized = django_filters.BooleanFilter()

  class Meta:
    model = Roll
    fields = ['id', 'status', 'finalized', 'notes', 'last_modified', 'event', 'trainee', 'submitted_by', 'date']


class AttendanceSerializer(BulkSerializerMixin, ModelSerializer):
  name = SerializerMethodField('get_trainee_name')
  individualslips = IndividualSlipSerializer(many=True,)
  groupslips = GroupSlipSerializer(many=True, source='groupslip')
  rolls = RollSerializer(many=True, source='current_rolls')

  class Meta(object):
    model = Trainee
    list_serializer_class = BulkListSerializer
    fields = ['name', 'individualslips', 'groupslips', 'rolls']

  def get_trainee_name(self, obj):
    return obj.__unicode__()


class RollsFinalizationSerializer(BulkSerializerMixin, ModelSerializer):

  class Meta(object):
    model = RollsFinalization
    list_serializer_class = BulkListSerializer
    fields = ['weeks']
