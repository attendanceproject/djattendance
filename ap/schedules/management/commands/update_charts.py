from django.core.management.base import BaseCommand
from schedules.models import Event
from seating.models import Chart


class Command(BaseCommand):

  # to use: python ap/manage.py update_charts --settings=ap.settings.dev
  def _update_charts(self):
  	main_classes = Event.objects.filter(class_type='MAIN')
  	main_chart = Chart.objects.get(name="Main")
  	for main_class in main_classes:
  		main_class.chart = main_chart
  		main_class.save()

  def handle(self, *args, **options):
    print("* Updating charts...")
    self._update_charts()  	
