# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from house_inspection.models import Inspectors, InspectableHouses, Scores
from accounts.models import Trainee
from django.contrib import messages
from django.shortcuts import redirect
from houses.models import House
from .forms import FaqForm, QuestionRequestCreateForm, HouseInspectionFaqAnswerForm, HouseInspectionFaqCommentForm, ScoresForm
from .models import HouseInspectionFaq, ItemizedInspectionReport
from terms.models import Term
from ap.base_datatable_view import BaseDatatableView
from django.views import generic
from django.core.urlresolvers import reverse_lazy
from aputils.trainee_utils import is_TA, trainee_from_user
from itertools import chain
from django.http import HttpResponseRedirect
from django.urls import reverse
from .utils import modify_question_status
from django.views.generic.edit import FormView
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

'''
def houseInspectionFaq(request):
  #template_name = 'house_inspection/faq.html'
  #model = FAQ
  #group_required = ['house_inspectors', 'training_assistant']
  # bound form
  if request.method == "POST":
    form = FaqForm(request.POST)
    if form.is_valid():
      question = form.cleaned_data['var']
      name = form.cleaned_data['name']

  form = FaqForm() #unbound form
  context = {    
    form
    #'page_title' = "FAQ",
    #'list_questions' = FAQ.objects.values('id', 'question', 'answer')
  }
  return render(request, 'house_inspection/faq.html', context)
'''

'''
This is the table under the cards.
'''

'''
class ItemizedInspectionReportJSON(BaseDatatableView):
  model = ItemizedInspectionReport
  columns = ['score_report.house', 'score_report.score', 'score_report.ric', 'score_report.date', 'score_report.inspectors', 'score_report.notes', 'score_report.uninspectable', 'score_report.uninspectable_reason',]
  max_display_length = 120

  
  def filter_queryset(self, qs):
    #search = self.request.GET.get(u'search[value]', None)
    ret = qs.none()
    if search:
      filters = []
      filters.append(Q(id=search))
      for f in filters:
        try:
          ret = ret | qs.filter(f)
        except ValueError:
          continue
      return ret
    else:
      return qs
'''
'''
class MyView(ListView):
    model = Update
    template_name = "updates/update.html"
    paginate_by = 10

    def get_queryset(self):
        filter_val = self.request.GET.get('filter', 'give-default-value')
        order = self.request.GET.get('orderby', 'give-default-value')
        new_context = Update.objects.filter(
            state=filter_val,
        ).order_by(order)
        return new_context

    def get_context_data(self, **kwargs):
        context = super(MyView, self).get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'give-default-value')
        context['orderby'] = self.request.GET.get('orderby', 'give-default-value')
        return context
'''

class ItemizedInspectionReport(generic.ListView):
  model = ItemizedInspectionReport
  template_name = 'house_inspection/itemized_inspection_report.html'

  def post(self, request, *args, **kwargs):
    return self.get(request, *args, **kwargs)

  def get_queryset(self):
    # filter by date
    filter_val = self.request.GET.get('filter', '')

    new_context = Foo.objects.filter(
        state = filter_val,
      )
    return new_context


  def get_context_data(self, **kwargs):
    context = super(ItemizedInspectionReport, self).get_context_data(**kwargs)
    # maybe go through inspectable hosues...
    #brothers_houses = InspectableHouses.objects.filter(residence_type='B')   
    context['scores'] = Scores.objects.filter(house__in=House.objects.filter(gender='B'))

    context['scores_s'] = Scores.objects.filter(house__in=House.objects.filter(gender='S'))



    return context

'''
class ItemizedInspectionReport(generic.ListView):
  model = ItemizedInspectionReport
  template_name = 'house_inspection/itemized_inspection_report.html'
  DataTableView = ItemizedInspectionReportJSON
  source_url = reverse_lazy("house_inspection:itemized_inspection_report-json")

  def get_queryset(self):
    #I think we edit the tables here or constrain them by gender
    qs = Scores.objects.all()
    return qs
  def get_context_data(self, **kwargs):
    # We can manipulate context data by gender/date
    context = super(ItemizedInspectionReport, self).get_context_data(**kwargs)
    scores = Scores.objects.none()
    scores = chain(scores, Scores.objects.all())
    
    context['scores'] = scores
    return context
'''

class QuestionRequestJSON(BaseDatatableView):
  model = HouseInspectionFaq
  columns = ['id', 'trainee', 'question', 'date_submitted', 'status',] # add date_submitted and status to model  
  order_columns = ['date_assigned',]  
  max_display_length = 120

  def filter_queryset(self, qs):
    search = self.request.GET.get(u'search[value]', None)
    ret = qs.none()
    if search:
      filters = []
      #filters.append(Q(trainee__firstname__icontains=search))
      #filters.append(Q(trainee__lastname__icontains=search))
      filters.append(Q(id=search))
      for f in filters:
        try:
          ret = ret | qs.filter(f)
        except ValueError:
          continue
      return ret
    else:
      return qs


class QuestionList(generic.ListView):
  model = HouseInspectionFaq
  template_name = 'house_inspection/question_list.html' #for TA or TOBI
  DataTableView = QuestionRequestJSON # goes to the class for the object
  source_url = reverse_lazy("house_inspection:house_inspection-json") # the url for the class QuestionRequestJSON

  # get the question and attached. Status should be U or A?
  def get_queryset(self):
    trainee = trainee_from_user(self.request.user)
    if is_TA(self.request.user) or (trainee.firstname == 'Tobi' and trainee.lastname == 'Abosede') or (trainee.firstname == 'Sofia' and trainee.lastname == 'Hunter'): # or Tobi or Hunter
      # FAQ.objects.filter(status='')
      qs = HouseInspectionFaq.objects.filter(status='U')|HouseInspectionFaq.objects.filter(status='A')|HouseInspectionFaq.objects.filter(status='An')
      return qs.order_by('date_assigned').order_by('status')
    else:
      trainee = trainee_from_user(self.request.user)
      qset = HouseInspectionFaq.objects.filter(trainee=trainee).order_by('status') #pretty sure this never works b/c trainee is an object while trainee_name is a string
    return qset

  def get_context_data(self, **kwargs):
    context = super(QuestionList, self).get_context_data(**kwargs)
    trainee = trainee_from_user(self.request.user)
    if is_TA(self.request.user) or (trainee.firstname == 'Tobi' and trainee.lastname == 'Abosede') or (trainee.firstname == 'Sofia' and trainee.lastname == 'Hunter'):
      faqs = HouseInspectionFaq.objects.none()
      for status in ['U', 'A', 'An', 'D']:
        faqs = chain(faqs, HouseInspectionFaq.objects.filter(status=status).filter(date_assigned__gte=Term.current_term().get_date(0, 0)).order_by('date_assigned').order_by('status'))
      context['faqs'] = faqs
    if not is_TA(self.request.user) and (trainee.firstname != 'Tobi' or trainee.lastname != 'Abosede') and (trainee.firstname != 'Sofia' or trainee.lastname != 'Hunter'):
      faqs = HouseInspectionFaq.objects.none()
      for status in ['A']:
        faqs = chain(faqs, HouseInspectionFaq.objects.filter(status=status).filter(date_assigned__gte=Term.current_term().get_date(0, 0)).order_by('date_assigned'))
      context['faqs'] = faqs
    return context

class FaqMixin(object): #maybe faq question submission mixin
  model = HouseInspectionFaq
  template_name = 'requests/request_form.html'
  form_class = QuestionRequestCreateForm
  success_url = reverse_lazy('house_inspection:question_list')

class FaqCreate(FaqMixin, generic.CreateView):
  def form_valid(self, form):
    req = form.save(commit=False)
    req.trainee = trainee_from_user(self.request.user)
    req.save()
    message = "Created new question request."
    messages.add_message(self.request, messages.SUCCESS, message)
    return super(FaqCreate, self).form_valid(form)



class FaqDetail(generic.DetailView):
  model = HouseInspectionFaq
  template_name = 'requests/detail_request.html'
  # the id of the url will give the details to this page.

class FaqUpdate(FaqMixin, generic.UpdateView):
  pass

class FaqDelete(FaqMixin, generic.DeleteView):
  def get_success_url(self):
    if self.get_object().trainee:
      return self.success_url
    return reverse_lazy('login')

class FaqAnswer(FaqMixin, generic.UpdateView):
  template_name = 'requests/ta_answer.html'
  form_class = HouseInspectionFaqAnswerForm
  raise_exception = True
  def form_valid(self, form):
    redirect_url = super(FaqAnswer, self).form_valid(form)
    obj = self.get_object()
    print obj.status 
    obj.status = 'An'
    print obj.status
    obj.save()
    return redirect_url

class FaqTaComment(FaqMixin, generic.UpdateView):
  template_name = 'requests/ta_comments.html'
  form_class = HouseInspectionFaqCommentForm
  raise_exception = True

class InspectorAnswer(FaqMixin, generic.UpdateView):
  template_name = 'requests/ta_answer.html'
  form_class = HouseInspectionFaqAnswerForm
  raise_exception = True
  def form_valid(self, form):
    redirect_url = super(InspectorAnswer, self).form_valid(form)
    obj = self.get_object()
    print obj.status 
    obj.status = 'An'
    print obj.status
    obj.save()
    return redirect_url

modify_status = modify_question_status(HouseInspectionFaq, reverse_lazy('house_inspection:question_list'))

def houseInspectionFaq(request):
  if request.method == "POST":
    form = FaqForm(request.POST)
    if form.is_valid():
      print("VALID")
      form.save()

  form = FaqForm() #unbound form
  return render(request, 'house_inspection/faq.html', {'form': form})

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
      inspectableHouses = InspectableHouses.objects.create(residence=house, residence_type=house.gender, uninspectable=False)
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
      if house.uninspectable == False:
        house.uninspectable = True
      else:
        house.uninspectable = False
      house.save()
  return render(request, 'house_inspection/manage_inspectable_houses.html', context)

class ManageScores(FormView):
  template_name = 'house_inspection/manage_scores.html'
  form_class = ScoresForm

  def get_success_url(self):
    return reverse('house_inspection:manage_scores')

  def form_valid(self, form):
    if form.is_valid():      
      house = form.cleaned_data.get('house')      
      date = form.cleaned_data.get('date')
      ric = form.cleaned_data.get('ric')
      inspectors = form.cleaned_data.get('inspectors')
      score = form.cleaned_data.get('score')
      notes = form.cleaned_data.get('notes')
      uninspectable_reason = form.cleaned_data.get('uninspectable_reason')
      uninspectable = False
      if uninspectable_reason:
        uninspectable = True      
      obj, created = Scores.objects.get_or_create(house=house, date=date, ric=ric, score=score, notes=notes, uninspectable_reason=uninspectable_reason, uninspectable=uninspectable)
      if created:        
        for inspector in inspectors:
          obj.inspectors.add(inspector)        
        obj.save()      
    return super(ManageScores, self).form_valid(form)

  def get_context_data(self, **kwargs):
    context = super(ManageScores, self).get_context_data(**kwargs)
    context ['page_title'] = 'Manage Scores'
    
    context ['scores'] = Scores.objects.all()
    return context

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