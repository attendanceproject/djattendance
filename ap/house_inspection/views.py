# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from house_inspection.models import FAQ, Inspectors
from aputils.decorators import group_required
from accounts.models import Trainee

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
  print inspectors
  context = {
    'inspectors': inspectors
  }
  return render(request, 'house_inspection/manage_inspectors.html', context)

def addInspector(request):
  if request.method == 'POST':
    # Get form values
    last_name = request.POST['last_name']
    first_name = request.POST['first_name']
    term = request.POST['term']
    prefect_number = request.POST['prefect_number']
    # Use a manual form do a search for a trainee to connect it. Actually change the whole model.
    # good
    if not Trainee.objects.filter(lastname=last_name,firstname=first_name).exists():
        # Error
        messages.error(request, 'That trainee does not exist')
        return redirect('house_inspection/manage_inspectors.html')
    else:    
      trainee = Trainee.objects.get(lastname=last_name,firstname=first_name)
      term = trainee.first().current_term
      inspector = Inspector.objects.create(last_name=last_name, first_name=first_name, term=term, prefect_number=prefect_number)
  return render(request, 'house_inspection/manage_inspectors.html', context)

'''
def register(request):
  if request.method == 'POST':
    # Get form values
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password2 = request.POST['password2']

    # Check if passwords match
    if password == password2:
      # Check username
      if User.objects.filter(username=username).exists():
        # Error
        messages.error(request, 'That username is taken')
        return redirect('register')
      else:
        # Check Email
        if User.objects.filter(email=email).exists():
          # Error
          messages.error(request, 'That email is being used')
          return redirect('register')
        else:
          # good
          user = User.objects.create_user(username=username, 
            password=password, email=email, first_name=first_name, last_name=last_name)
          # Login after register example
          # auth.login(request, user)
          # messages.success(request, 'You are now logged in')
          user.save()
          messages.success(request, 'You are now registered and can log in')
          return redirect('login')
    else:
      # error
      messages.error(request, 'Passwords do not match')
      return redirect('register')
  else:   
    return render (request, 'accounts/register.html')
'''





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
