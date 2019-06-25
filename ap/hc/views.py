from datetime import datetime

from accounts.models import Trainee
from aputils.decorators import group_required
from braces.views import GroupRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView, UpdateView
from terms.models import Term

from .forms import (HCRecommendationAdminForm, HCRecommendationForm,
                    HCSurveyAdminForm, HCSurveyForm, HCTraineeCommentForm)
from .models import (HCRecommendation, HCRecommendationAdmin, HCSurvey,
                     HCSurveyAdmin, HCTraineeComment, House)

HCSA_FORM = 'hcsa_form'
HCRA_FORM = 'hcra_form'


class HCSurveyAdminCreate(GroupRequiredMixin, TemplateView):
  model = HCSurveyAdmin
  template_name = 'hc_admin/hc_admin.html'
  form_class = HCSurveyAdminForm
  second_form_class = HCRecommendationAdminForm
  group_required = ['training_assistant']
  success_url = reverse_lazy('hc:hc-admin')

  def form_valid(self, form):
    term = Term.current_term()
    index = len(HCSurveyAdmin.objects.filter(term=term)) + 1
    hcsa = form.save(commit=False)
    hcsa.term = term
    hcsa.index = index
    hcsa.save()
    return HttpResponseRedirect(self.success_url)

  def form_invalid(self, **kwargs):
    return self.render_to_response(self.get_context_data(**kwargs))

  def post(self, request, *args, **kwargs):
    # determine which form is being submitted
    # uses the name of the form's submit button
    if HCSA_FORM in request.POST:
      form = self.form_class(request.POST)
      form_name = HCSA_FORM
      if form.is_valid():
        return self.form_valid(form)
      else:
        return self.form_invalid(form)

    else:
      # get the secondary form
      form = self.second_form_class(request.POST)
      form_name = HCRA_FORM
      if form.is_valid():
        hcra = HCRecommendationAdmin.objects.get_or_create(term=Term.current_term())[0]
        hcra.open_time = form.cleaned_data['open_time']
        hcra.close_time = form.cleaned_data['close_time']
        hcra.open_survey = form.cleaned_data['open_survey']
        hcra.save()
        return HttpResponseRedirect(self.success_url)
      else:
        return self.form_invalid(**{form_name: form})

  def get_context_data(self, **kwargs):
    ctx = super(HCSurveyAdminCreate, self).get_context_data(**kwargs)
    term = Term.current_term()
    hcra = HCRecommendationAdmin.objects.get_or_create(term=term)[0]
    if HCSA_FORM not in ctx:
      ctx[HCSA_FORM] = self.form_class(auto_id="hcsa_%s")
    if HCRA_FORM not in ctx:
      ctx[HCRA_FORM] = self.second_form_class(instance=hcra, auto_id="hcra_%s")

    ctx['hc_admins'] = HCSurveyAdmin.objects.filter(term=term).order_by('-index')
    init_open_datetime = hcra.open_time
    init_close_datetime = hcra.close_time

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
  group_required = ['training_assistant']
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


class HCRecommendationCreate(GroupRequiredMixin, TemplateView):
  model = HCRecommendation
  template_name = 'hc/hc_recommendation.html'
  form_class = HCRecommendationForm
  group_required = ['HC']
  success_url = reverse_lazy('home')
  admin_model = HCRecommendationAdmin

  def get_context_data(self, **kwargs):
    ctx = super(HCRecommendationCreate, self).get_context_data(**kwargs)

    survey_admin = self.admin_model.objects.get_or_create(term=Term.current_term())[0]
    house = House.objects.get(id=self.request.user.house.id)
    eligible_hcs = house.residents.exclude(groups__name="HC").filter(current_term__in=[2, 3])
    hc_recommendation_forms = []
    for trainee in eligible_hcs:
      try:
        hcr = HCRecommendation.objects.get(recommended_hc=trainee, survey_admin=survey_admin)
        hcr_form = HCRecommendationForm(house=house, instance=hcr)
      except HCRecommendation.DoesNotExist:
        hcr_form = HCRecommendationForm(house=house, initial={'recommended_hc': trainee})

      hc_recommendation_forms.append(hcr_form)

    ctx['button_label'] = 'Submit'
    ctx['page_title'] = 'HC Recommendation'
    ctx['hc'] = Trainee.objects.get(id=self.request.user.id)
<<<<<<< HEAD
    ctx['house'] = House.objects.get(id=self.request.user.house.id)
    hcrs = HCRecommendation.objects.filter(house=ctx['house'])
    ctx['hcrs'] = JSONRenderer().render(HCRecommendationSerializer(hcrs, many=True).data).decode('utf-8')
    ctx['form'] = HCRecommendationForm(user=self.request.user)
    survey_admin = self.admin_model.objects.get_or_create(term=Term.current_term())[0]
=======
    ctx['house'] = house
    ctx['hc_recommendation_forms'] = hc_recommendation_forms
>>>>>>> dev
    # if survey is open, but not within time range -> read-only
    if (datetime.now() > survey_admin.close_time or datetime.now() < survey_admin.open_time) and survey_admin.open_survey:
      ctx['read_only'] = True

    return ctx

  def post(self, request, *args, **kwargs):
    survey_admin = self.admin_model.objects.get_or_create(term=Term.current_term())[0]

    recommended_hcs = request.POST.getlist("recommended_hc")
    choices = request.POST.getlist("choice")
    recommendations = request.POST.getlist("recommendation")

    for i in range(len(recommended_hcs)):
      form_data = {}
      form_data['recommended_hc'] = Trainee.objects.get(id=recommended_hcs[i])
      form_data['choice'] = choices[i]
      form_data['recommendation'] = recommendations[i]

      check_existing = HCRecommendation.objects.filter(survey_admin=survey_admin, recommended_hc=form_data["recommended_hc"])
      if check_existing.count() != 0:
        # if existing then delete and make new ones, don't bother editing
        # not the safest thing in the world but this is a low risk module so yeah.
        check_existing.delete()

      hcr = HCRecommendation(**form_data)
      hcr.survey_admin = survey_admin
      hcr.hc = self.request.user
      hcr.house = self.request.user.house
      hcr.save()

    return HttpResponseRedirect(reverse_lazy('hc:hc-recommendation'))


class HCSurveyTAView(GroupRequiredMixin, TemplateView):
  template_name = 'ta/hc_survey_ta_view.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    index = self.kwargs.get('index')
    context = super(HCSurveyTAView, self).get_context_data(**kwargs)
    hcsa = HCSurveyAdmin.objects.filter(term=Term.current_term()).filter(index=index)
    surveys_and_comments = []
    house_ids = HCSurvey.objects.filter(survey_admin=hcsa, submitted=True).values_list('house', flat=True)
    for hcs in HCSurvey.objects.filter(survey_admin=hcsa, submitted=True).exclude(house__gender='C').order_by('house__gender', 'house__name'):
      surveys_and_comments.append({
        'survey': hcs,
        'trainee_comments': HCTraineeComment.objects.filter(hc_survey=hcs)
      })
    context['bro_reported'] = House.objects.filter(id__in=house_ids, gender="B")
    context['bro_not_reported'] = House.objects.exclude(id__in=house_ids).filter(gender="B")
    context['sis_reported'] = House.objects.filter(id__in=house_ids, gender="S")
    context['sis_not_reported'] = House.objects.exclude(id__in=house_ids).filter(gender="S")
    context['surveys_and_comments'] = surveys_and_comments
    context['survey_number'] = index
    context['page_title'] = "HC Survey Report"
    return context


class HCRecommendationTAView(GroupRequiredMixin, TemplateView):
  template_name = 'ta/hc_recommendation_ta_view.html'
  group_required = ['training_assistant']

  def get_context_data(self, **kwargs):
    context = super(HCRecommendationTAView, self).get_context_data(**kwargs)
    hcra = HCRecommendationAdmin.objects.get(term=Term.current_term())
    houses = House.objects.exclude(gender='C').order_by('gender', 'name')
    hc_recommendations = []
    for h in houses:
      hcrs = HCRecommendation.objects.filter(survey_admin=hcra, house=h)
      expected = h.residents.exclude(groups__name='HC').filter(current_term__in=[2, 3]).count()
      hc_recommendations.append({
        'house': h,
        'hcrs': hcrs,
        'submitted': hcrs.count(),
        'expected': expected,
      })
    context['hc_recommendations'] = hc_recommendations
    context['page_title'] = "HC Recommendations Report"
    return context
