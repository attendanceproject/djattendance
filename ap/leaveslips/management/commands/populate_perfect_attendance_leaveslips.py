from django.core.management.base import BaseCommand
from leaveslips.models import IndividualSlip, GroupSlip

class Command(BaseCommand):
  # to use: python ap/manage.py populate_perfect_attendance_leaveslips --settings=ap.settings.dev
  def _update_leaveslips(self):
    LS_TYPES = ['SERV', 'CONF', 'TTRIP', 'FWSHP']
    IndividualSlip.objects.filter(type__in=LS_TYPES).update(does_not_count=True)
    GroupSlip.objects.filter(type__in=LS_TYPES).update(does_not_count=True)

  def handle(self, *args, **options):
    # print("* Updating leave slips...")
    self._update_leaveslips()
