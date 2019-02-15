from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from services.models.service_hours import ServiceAttendance
from services.models.worker import Worker
from terms.models import Term


# run populate_services before this script
class Command(BaseCommand):
  # to use: python ap/manage.py populate_designated_services --settings=ap.settings.dev

  def _create_attendance(self):
    workers = Worker.objects.filter(trainee__is_active=True)
    current_term = Term.current_term()
    week_range = range(0, current_term.term_week_of_date(date.today()))
    for worker in workers:
      services = worker.designated.all()
      for service in services:
        for week in week_range:
          service_attendance = ServiceAttendance.objects.get_or_create(designated_service=service, worker=worker, term=current_term, week=week)[0]
          service_attendance.excused = True
          service_attendance.save()

  def _delete_duplicates(model, unique_fields):  # id/pk is always unique, so don't include it in unique_fields
    from django.db.models import Count, Min
    ret = []
    # finds a duplicates and gets the lower pk value of each duplicate
    master_pks = model.objects.values(*unique_fields).annotate(Min('pk'), count=Count('pk')).filter(count__gt=1).values_list('pk__min', flat=True)
    # gets a dict of {id: object_to_keep}
    masters = model.objects.in_bulk(list(master_pks))
    for master in masters.values():  # for each object
      # create a filter dictionary of {field: mater_object_value}
      d = dict(zip(unique_fields, [getattr(master, f) for f in unique_fields]))
      # get duplicates, filter out the pk we are keeping and delete the rest
      to_delete = model.objects.filter(**d).exclude(pk=master.pk)
      print to_delete
      msg = to_delete.delete()
      ret.append(msg)
    return ret

  def handle(self, *args, **options):
    print('* Creating service attendance objects...')
    self._create_attendance()


def get_next_tuesday():
  today = datetime.now().date()
  t = timedelta((12 - today.weekday()) % 7)  # Mon-0, Sun-6
  return today + t
