from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.contrib import messages
from meal_seating.models import Table, TraineeExclusion
from accounts.models import Trainee
from datetime import date, timedelta
from django.views import generic
from .serializers import TableSerializer

from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer


@csrf_protect
def editinfo(request):
  test = request.POST.getlist('to')
  print test
  isChecked = [int(x) for x in request.POST.getlist('to[]')]
  print set(isChecked)
  exclude_list = get_exclude_list()
  difference = set(exclude_list) - set(isChecked)
  addition = set(isChecked) - set(exclude_list)
  TraineeExclusion.objects.all().filter(trainee__in=list(difference)).delete()
  trainee_exclusions = [TraineeExclusion(trainee=val) for val in addition]
  TraineeExclusion.objects.bulk_create(trainee_exclusions)
  return HttpResponse(difference)


def get_exclude_list():
  exclude_list = TraineeExclusion.objects.values_list('trainee', flat=True)
  return exclude_list if exclude_list else []


def seattables(request):
  filterchoice = request.POST['Filter']
  genderchoice = request.POST['Gender']
  startdate = request.POST['startdate']
  enddate = request.POST['enddate']

  trainees = Trainee.objects.all().filter(gender=genderchoice).order_by(filterchoice).exclude(id__in=get_exclude_list())
  #date_of_birth will sort by year by default, so the following code will make it order by month,day
  if filterchoice == 'date_of_birth':
	trainees = Trainee.objects.all().filter(gender=genderchoice).extra(select={
        'birth_date_month': 'EXTRACT(MONTH FROM date_of_birth)',
        'birth_date_day': 'EXTRACT(DAY FROM date_of_birth)'
    },
    order_by=['birth_date_month','birth_date_day']).exclude(id__in=get_exclude_list())
  seating_list = seatinglist(trainees, genderchoice)
  if seating_list is None:
    messages.error(request, 'Not enough seats available!')
    return redirect('/meal_seating')
  else:
    return render(request, 'meal_seating/detail.html', {'seating_list': seating_list, 'startdate': startdate, 'enddate': enddate})


def newseats(request):
  exclude_list = get_exclude_list()
  trainees_exclude = Trainee.objects.filter(pk__in=exclude_list)
  trainees = Trainee.objects.filter(is_active=1).exclude(type="S").order_by("lastname")
  return render(request, 'meal_seating/index.html', {'trainees': trainees, 'exclude_list': trainees_exclude, })


def signin(request):
  trainees = Trainee.objects.all().filter(is_active=1).order_by("lastname")
  startdate = date.today()
  two_week_datelist = []
  for x in range(0, 14):
    mydate = startdate + timedelta(days=x)
    two_week_datelist.append(format(mydate))
  return render(request, 'meal_seating/mealsignin.html', {'trainees': trainees, 'start_date': startdate, "two_week_datelist": two_week_datelist})


def seatinglist(genderlist, gender):
    tables = Table.objects.filter(gender=gender)
    traineenum = 0
    tablenum = 0
    totalcapacity = 0
    traineecount = len(genderlist)
    for x in Table.objects.all().filter(gender=gender).values("capacity"):
      totalcapacity += x["capacity"]
    if (traineecount > totalcapacity):
      print "cannot seat ", traineecount, " trainees. Current capacity is: ", totalcapacity
      return None
    else:
      # Make columns have max 55 trainees.
      # rows will contain meal_seating.
      mealCols = []
      mealRows = []
      maxRowPerCol = 55
      for trainee in genderlist:
        meal_seating = {}
        if traineenum == tables[tablenum].capacity:
          tablenum += 1
          traineenum = 0
        meal_seating["first_name"] = trainee.firstname
        meal_seating["last_name"] = trainee.lastname
        meal_seating["table"] = tables[tablenum]
        mealRows.append(meal_seating)
        traineenum += 1
      sortedMealRows = sorted(mealRows, key=lambda k: (k["last_name"],k["first_name"]))
      #numCols is how many columns resulting table will have
      numCols = traineecount/maxRowPerCol + 1
      #the rare case that maxRowPerCol divides traineecount
      if (traineecount % maxRowPerCol) == 0:
          numCols -= 1
      colNum = 1
      while colNum <= numCols :
          mealCols.append(sortedMealRows[maxRowPerCol * (colNum - 1):maxRowPerCol * colNum])
          colNum += 1
      return mealCols


class TableListView(generic.ListView):
  model = Table
  template_name = 'meal_seating/table_edit.html'

  context_object_name = 'context'

  def get_context_data(self, **kwargs):
    listJSONRenderer = JSONRenderer()
    l_render = listJSONRenderer.render
    table = Table.objects.all().order_by('name')
    context = super(TableListView, self).get_context_data(**kwargs)
    context['table_bb'] = l_render(TableSerializer(table, many=True).data)
    return context


class TableViewSet(viewsets.ModelViewSet):
  """
  API endpoint that allows tables to be viewed or edited.
  """
  queryset = Table.objects.all()
  serializer_class = TableSerializer
