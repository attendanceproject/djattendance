from datetime import datetime

from accounts.models import Trainee
from aputils.decorators import group_required
from braces.views import GroupRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from terms.models import Term

from .forms import (HCRecommendationAdminForm, HCRecommendationForm,
                    HCSurveyAdminForm, HCSurveyForm, HCTraineeCommentForm)
from .models import (HCRecommendation, HCRecommendationAdmin, HCSurvey,
                     HCSurveyAdmin, HCTraineeComment, House)


class HCSurveyAdminCreate(GroupRequiredMixin, CreateView):
  model = HCSurveyAdmin
  template_name = 'hc_admin/hc_admin.html'
  form_class = HCSurveyAdminForm
  second_form_class = HCRecommendationAdminForm
  group_required = ['training_assistant']
  success_url = reverse_lazy('hc:hc-admin')

  def post(self, request, *args, **kwargs):

    # determine which form is being submitted
    # uses the name of the form's submit button

    if 'hcsa_form' in request.POST:
      form = self.form_class(request.POST)
      if form.is_valid():
        return self.form_valid(form)
      else:
        return self.form_invalid(form)

    else:
      # get the secondary form
      form = self.second_form_class(request.POST)
      if form.is_valid():
        hcra = HCRecommendationAdmin.objects.get_or_create(term=Term.current_term())[0]
        for house in House.objects.all():
          hcr = HCRecommendation.objects.get_or_create(house=house, survey_admin=hcra)[0]
          hcr.open_time = form.cleaned_data['open_time']
          hcr.close_time = form.cleaned_data['close_time']
          hcr.save()
        hcra.open_time = form.cleaned_data['open_time']
        hcra.close_time = form.cleaned_data['close_time']
        hcra.open_survey = form.cleaned_data['open_survey']
        hcra.save()
        return HttpResponseRedirect(self.success_url)
      else:
        return self.form_invalid(form)

  def form_valid(self, form):
    term = Term.current_term()
    index = len(HCSurveyAdmin.objects.filter(term=term)) + 1
    hcsa = form.save(commit=False)
    hcsa.term = term
    hcsa.index = index
    hcsa.save()
    return super(HCSurveyAdminCreate, self).form_valid(form)

  def get_context_data(self, **kwargs):
    ctx = super(HCSurveyAdminCreate, self).get_context_data(**kwargs)
    term = Term.current_term()

    ctx['hc_admins'] = HCSurveyAdmin.objects.filter(term=term).order_by('-index')
    ctx['hcra_form'] = HCRecommendationAdminForm()
    ctx['hcsa_form'] = ctx['form']
    init_open_datetime = HCRecommendationAdmin.objects.get_or_create(term=term)[0].open_time
    init_close_datetime = HCRecommendationAdmin.objects.get_or_create(term=term)[0].close_time

    if init_open_datetime is None or init_close_datetime is None:
      ctx['button_label2'] = 'Create Recommendation'
    else:
      ctx['init_open_datetime'] = init_open_datetime.strftime("%m/%d/%Y %H:%M")
      ctx['init_close_datetime'] = init_close_datetime.strftime("%m/%d/%Y %H:%M")
      ctx['button_label2'] = 'Update Recommendation'

    ctx['button_label1'] = 'Create Survey'
    ctx['page_title'] = 'HC Survey Admin'
    return ctx


class HCSurveyAdminUpdate(UpdateView):
  model = HCSurveyAdmin
  template_name = 'hc_admin/admin_hc_surveys_update.html'
  form_class = HCSurveyAdminForm
  success_url = reverse_lazy('hc:hc-admin')

  def get_context_data(self, **kwargs):
    ctx = super(HCSurveyAdminUpdate, self).get_context_data(**kwargs)
    ctx['hc_admins'] = HCSurveyAdmin.objects.filter(term=Term.current_term()).order_by('-index')
    ctx['update'] = True
    ctx['hcsa_form'] = ctx['form']
    ctx['page_title'] = 'Update HC Survey'
    ctx['button_label1'] = 'Update'
    return ctx


class HCSurveyAdminDelete(GroupRequiredMixin, DeleteView, SuccessMessageMixin):
  model = HCSurveyAdmin
  success_url = reverse_lazy('hc:hc-admin')
  group_required = [u'training_assistant']
  success_message = "HC Surveys have been deleted."


@group_required(['HC'])
def submit_hc_survey(request):
  hc = request.user
  house = House.objects.get(id=hc.house.id)
  term = Term.current_term()
  hcsa = HCSurveyAdmin.objects.filter(term=term).order_by("-index")[0]
  residents = Trainee.objects.filter(house=house).exclude(groups__name='HC')

  if request.method == 'POST':
    data = request.POST

    # build forms from data
    # get_or_create allows you to create/update data
    # HCSurvey -- one per house per period
    temp1, created = HCSurvey.objects.get_or_create(house=house, survey_admin=hcsa)

    hc_survey_form = HCSurveyForm(data, instance=temp1, auto_id=True)
    comment_forms = []

    for trainee in residents:
      # Comment -- one per trainee per period
      temp2, created = HCTraineeComment.objects.get_or_create(hc_survey=temp1, trainee=trainee)
      comment_forms.append(
        HCTraineeCommentForm(data, prefix=trainee.id, instance=temp2, auto_id=True)
      )

    # validate forms & save objects
    if hc_survey_form.is_valid() and all(cf.is_valid() for cf in comment_forms):
      hc_survey = hc_survey_form.save(commit=False)
      hc_survey.hc = hc
      hc_survey.house = house
      hc_survey.survey_admin = hcsa
      hc_survey.submitted = True
      hc_survey.save()

      for cf in comment_forms:
        comment = cf.save(commit=False)
        comment.hc_survey = hc_survey
        comment.trainee = residents.get(id=cf.prefix)
        comment.save()

    return HttpResponseRedirect(reverse_lazy('hc:hc-survey'))

  else:  # GET

    # build forms
    temp1 = HCSurvey.objects.get_or_create(house=house, survey_admin=hcsa)[0]
    form = HCSurveyForm(instance=temp1, auto_id=True)
    comment_forms = []
    for trainee in residents:
      temp2 = HCTraineeComment.objects.get_or_create(hc_survey=temp1, trainee=trainee)[0]
      comment_forms.append(
        (trainee, HCTraineeCommentForm(prefix=trainee.id, instance=temp2))
      )

    # logic check in case user doesn't input close or open time, does not consider none times
    # eg: if there's only open time, only check if now is after open time
    read_only = False
    if hcsa.open_survey:
      # check open and closse times
      if hcsa.open_time:
        if datetime.now() < hcsa.open_time:
          read_only = True
      elif hcsa.close_time:
        if datetime.now() > hcsa.close_time:
          read_only = True

    ctx = {
      'form': form,
      'comment_forms': comment_forms,
      'button_label': "Submit",
      'page_title': "HC Survey",
      'period': hcsa.index,
      'house': house,
      'hc': hc,
      'read_only': read_only,
      'due': hcsa.close_time
    }
    return render(request, 'hc/hc_survey.html', context=ctx)


class HCRecommendationCreate(GroupRequiredMixin, UpdateView):
  model = HCRecommendation
  template_name = 'hc/hc_recommendation.html'
  form_class = HCRecommendationForm
  group_required = ['HC']
  success_url = reverse_lazy('home')
  admin_model = HCRecommendationAdmin

  def get_object(self, queryset=None):
    # get the existing object or created a new one
    hcra = self.admin_model.objects.get_or_create(term=Term.current_term())[0]
    obj, created = self.model.objects.get_or_create(house=self.request.user.house, survey_admin=hcra)
    return obj

  def get_form_kwargs(self):
    kwargs = super(HCRecommendationCreate, self).get_form_kwargs()
    kwargs['user'] = self.request.user
    return kwargs

  def form_valid(self, form):
    hc_recommendation = form.save(commit=False)
    hc_recommendation.survey_admin = self.admin_model.objects.get_or_create(term=Term.current_term())[0]
    hc_recommendation.hc = self.request.user
    hc_recommendation.house = self.request.user.house
    hc_recommendation.save()
    return super(HCRecommendationCreate, self).form_valid(form)

  def get_context_data(self, **kwargs):
    ctx = super(HCRecommendationCreate, self).get_context_data(**kwargs)
    ctx['button_label'] = 'Submit'
    ctx['page_title'] = 'HC Recommendation'
    ctx['hc'] = Trainee.objects.get(id=self.request.user.id)
    ctx['house'] = House.objects.get(id=self.request.user.house.id)
    obj = self.get_object()
    # if survey is open, but not within time range -> read-only
    if (datetime.now() > obj.survey_admin.close_time or datetime.now() < obj.survey_admin.open_time) and obj.survey_admin.open_survey:
      ctx['read_only'] = True
    return ctx


class HCRecommendationUpdate(HCRecommendationCreate, UpdateView):
  model = HCRecommendation
  template_name = 'hc/hc_recommendation.html'
  form_class = HCRecommendationForm
  success_url = reverse_lazy('home')

  def get_context_data(self, **kwargs):
    ctx = super(HCRecommendationUpdate, self).get_context_data(**kwargs)
    ctx['button_label'] = 'Update'
    ctx['page_title'] = 'Update HC Recommendation'
    return ctx


class HCSurveyTAView(GroupRequiredMixin, TemplateView):
  template_name = 'ta/hc_survey_ta_view.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    index = self.kwargs.get('index')
    context = super(HCSurveyTAView, self).get_context_data(**kwargs)
    hcsa = HCSurveyAdmin.objects.filter(term=Term.current_term()).filter(index=index)
    surveys_and_comments = []
    house_ids = HCSurvey.objects.filter(survey_admin=hcsa, submitted=True).values_list('house', flat=True)
    for hcs in HCSurvey.objects.filter(survey_admin=hcsa, submitted=True).exclude(house__gender='C').order_by('house__gender'):
      surveys_and_comments.append({
        'survey': hcs,
        'trainee_comments': HCTraineeComment.objects.filter(hc_survey=hcs)
      })
    context['bro_reported'] = House.objects.filter(id__in=house_ids, gender="B")
    context['bro_not_reported'] = House.objects.exclude(id__in=house_ids).filter(gender="B")
    context['sis_reported'] = House.objects.filter(id__in=house_ids, gender="S")
    context['sis_not_reported'] = House.objects.exclude(id__in=house_ids).filter(gender="S")
    context['surveys_and_comments'] = surveys_and_comments
    context['page_title'] = "HC Survey Report"
    return context


class HCRecommendationTAView(GroupRequiredMixin, TemplateView):
  template_name = 'ta/hc_recommendation_ta_view.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    context = super(HCRecommendationTAView, self).get_context_data(**kwargs)
    hcra = HCRecommendationAdmin.objects.filter(term=Term.current_term())
    context['hc_recommendations'] = HCRecommendation.objects.filter(survey_admin=hcra)
    context['page_title'] = "HC Recommendations Report"
    return context
