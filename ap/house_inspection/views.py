# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from house_inspection.models import FAQ, Inspectors, InspectableHouses
from aputils.decorators import group_required
from accounts.models import Trainee
from django.contrib import messages
from django.shortcuts import redirect
from houses.models import House


'''
class HouseInspectionFaq(TemplateView):
  template_name = 'house_inspection/faq.html'  
  model = FAQ
  group_required = ['house_inspectors', 'training_assistant']

  def get_context_data(self, **kwargs)  :
  	context = super(HouseInspectionFaq, self).get_context_data(**kwargs)
  	context['page_title'] = "FAQ"
  	context['list_questions'] = FAQ.objects.values('id', 'question', 'answer')

  	return context
'''

def houseInspectionFaq(request):
  #template_name = 'house_inspection/faq.html'  
  #model = FAQ
  group_required = ['house_inspectors', 'training_assistant']
  context = {
    #'page_title' = "FAQ",
    #'list_questions' = FAQ.objects.values('id', 'question', 'answer')
  }
  return render(request, 'house_inspection/faq.html', context)

def manageInspectors(request):
  inspectors = Inspectors.objects.order_by('-last_name')  
  context = {
    'inspectors': inspectors
  }
  if request.method == 'POST':   
    # Get form values    
    last_name = request.POST['last_name']
    first_name = request.POST['first_name']        
    prefect_number = request.POST['prefect_number']
    # Use a manual form do a search for a trainee to connect it. Actually change the whole model.    
    if not Trainee.objects.filter(lastname=last_name,firstname=first_name).exists():
        # Error        
        messages.error(request, 'That trainee does not exist')
        return redirect('house_inspection:manage_inspectors')
    elif Inspectors.objects.filter(last_name=last_name,first_name=first_name).exists():      
      messages.error(request, 'The Inspector already exists')
      return redirect('house_inspection:manage_inspectors')
    else:          
      trainee = Trainee.objects.get(lastname=last_name,firstname=first_name)      
      term = trainee.current_term  
      last_name = trainee.lastname
      first_name = trainee.firstname
      inspector = Inspectors.objects.create(trainee=trainee, last_name=last_name, first_name=first_name,term=term,prefect_number=prefect_number)
      inspector.save()
  
  return render(request, 'house_inspection/manage_inspectors.html', context)

def manageInspectableHouses(request):
  houses = House.objects.all()  
  for house in houses:
    #create this in admin
    if not InspectableHouses.objects.filter(residence=house).exists():
      inspectableHouse = InspectableHouses.objects.create(residence=house, residence_type=house.gender, uninspectable=False)
  inspectableHouses = InspectableHouses.objects.order_by('-residence')
  context = {
    'inspectableHouses': inspectableHouses
  }
  if request.method == 'POST':
    # Get Uninspectable
    # Get the house
    print 'HOUSE CHANGE'
    list_of_checks = request.POST.getlist('checks[]')
    print list_of_checks
    for house_id in list_of_checks:
      print house_id
      house = InspectableHouses.objects.get(id=house_id)
      print house
      house.uninspectable = True
      house.save()
  return render(request, 'house_inspection/manage_inspectable_houses.html', context)

'''
class MyFormView(View):
    form_class = MyForm
    initial = {'key': 'value'}
    template_name = 'form_template.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})
'''
