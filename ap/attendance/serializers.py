import django_filters
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Roll
from rest_framework import filters
from datetime import *
from django.db.models import Q
from accounts.models import Trainee
from leaveslips.models import IndividualSlip
from leaveslips.serializers import IndividualSlipSerializer, GroupSlipSerializer
from aputils.trainee_utils import trainee_from_user
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)


class RollSerializer(BulkSerializerMixin, ModelSerializer):

  class Meta(object):
    model = Roll
    list_serializer_class = BulkListSerializer
    fields = ['id', 'event', 'trainee', 'status', 'finalized', 'notes', 'last_modified', 'submitted_by', 'date']

  def create(self, validated_data):
    trainee = validated_data['trainee']
    event = validated_data['event']
    date = validated_data['date']
    submitted_by = self.context['request'].user
    validated_data['submitted_by'] = submitted_by
    status = validated_data['status']

    # checks if roll exists for given trainee, event, and date
    roll_override = Roll.objects.filter(trainee=trainee, event=event.id, date=date)
    leaveslips = IndividualSlip.objects.filter(rolls=roll_override)


    if roll_override.count() == 0 and status != 'P':  # if no pre-existing rolls, create
      return Roll.objects.create(**validated_data)
    elif roll_override.count() == 1:  # if a roll already exists,
      # no changes if there's no status change
      if status == roll_override.first().status:
        return validated_data

      if status == 'P' and not leaveslips.exists():  # if input roll is "P" and no leave slip, delete it
        roll_override.delete()
        return validated_data
      roll = roll_override.first()
      if roll.trainee.self_attendance and (roll.trainee != submitted_by):
        return Roll.objects.create(**validated_data)
      elif roll.trainee.self_attendance and (roll.trainee == submitted_by):
        roll_override.update(**validated_data)
        roll_override.update(last_modified=datetime.now())
        return validated_data
      elif not roll.trainee.self_attendance:
        roll_override.update(**validated_data)
        return validated_data
      return validated_data
    elif roll_override.count() == 2:  # if duplicate rolls
      if trainee.self_attendance:
        r = roll_override.filter(submitted_by=submitted_by).first()
      else:
        r = roll_override.filter(~Q(submitted_by=submitted_by)).first()

      if r and r.status != status:
        r.status = status
        r.submitted_by = self.context['request'].user
        r.last_modified = datetime.now()
        r.save()
      return validated_data
    else:
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
  rolls = RollSerializer(many=True,)

  class Meta(object):
    model = Trainee
    list_serializer_class = BulkListSerializer
    fields = ['name', 'individualslips', 'groupslips', 'rolls']

  def get_trainee_name(self, obj):
    return obj.__unicode__()
