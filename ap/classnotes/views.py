from datetime import datetime, time

from accounts.models import Trainee
from aputils.trainee_utils import trainee_from_user
from audio.models import AudioFile
from classnotes.utils import assign_classnotes
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from schedules.models import Event
from terms.models import Term

from .forms import ApproveClassnotesForm, EditClassnotesForm, NewClassnotesForm
from .models import Classnotes
from .serializers import ClassnotesSerializer


class ClassnotesSingleTraineeView(TemplateView):
  template_name = 'classnotes/classnotes_singletrainee.html'

  def post(self, request, *args, **kwargs):
    if 'approve' in request.POST:
      for value in request.POST.getlist('selection'):
        classnotes = Classnotes.objects.get(pk=value)
        classnotes.approve()
      messages.success(request, "Checked Class notes(s) Approved!")
    if 'hard_copy_approve' in request.POST:
      for value in request.POST.getlist('selection'):
        classnotes = Classnotes.objects.get(pk=value)
        classnotes.hard_copy_approve()
      messages.success(request, "Checked Class notes(s) Hard-copy Approved!")
    if 'delete' in request.POST:
      for value in request.POST.getlist('selection'):
        Classnotes.objects.get(pk=value).delete()
      messages.success(request, "Checked Class notes(s) Deleted!")
    return self.get(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(ClassnotesSingleTraineeView, self).get_context_data(**kwargs)
    trainee_id = self.request.GET.get('trainee_list', -1)
    trainee = Trainee.objects.get(id=trainee_id) if trainee_id > 0 else Trainee.objects.first()
    classnotes = Classnotes.objects.filter(trainee=trainee)
    if classnotes.exists():
      detail = {}
      for ev in Event.objects.filter(type='C'):
        for_ev = classnotes.filter(event=ev)
        count = for_ev.count()
        if count > 0:
          owed = count - for_ev.filter(status='U').count()
          detail[ev.name] = {'count': count, 'owed': owed}
    else:
      detail = None

    context['selected_trainee'] = trainee
    context['trainee_list'] = Trainee.objects.values('id', 'firstname', 'lastname')
    context['detail'] = detail
    context['classnotes_other'] = classnotes.filter(status='A')
    context['classnotes_pending'] = classnotes.filter(Q(status='F') | Q(status='P') | Q(status='U')).order_by('status')
    return context


class ClassnotesListView(ListView):
  template_name = 'classnotes/classnotes_list.html'
  model = Classnotes
  conext_object_name = 'classnotes_list'

  # Lock this method for TA only
  def post(self, request, *args, **kwargs):
    """
    'approve' when an approve button is pressed 'delete' when a delete
    button is pressed 'assign_classnotes' when assigning classnotes
    """
    if 'approve' in request.POST:
      for value in request.POST.getlist('selection'):
        classnotes = Classnotes.objects.get(pk=value)
        classnotes.approve()
      messages.success(request, "Checked Class notes(s) Approved!")
    if 'hard_copy_approve' in request.POST:
      for value in request.POST.getlist('selection'):
        classnotes = Classnotes.objects.get(pk=value)
        classnotes.hard_copy_approve()
      messages.success(request, "Checked Class notes(s) Hard-copy Approved!")
    if 'delete' in request.POST:
      for value in request.POST.getlist('selection'):
        Classnotes.objects.get(pk=value).delete()
      messages.success(request, "Checked Class notes(s) Deleted!")
    if 'assign_classnotes' in request.POST:
      # term = Term.current_term()
      assign_classnotes()
      messages.success(request, "Class notes assigned according to attendance!")
    return self.get(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(ClassnotesListView, self).get_context_data(**kwargs)
    user = self.request.user
    if user.type == 'R':
      classnotes = Classnotes.objects.filter(trainee=user)
      context['classnotes'] = classnotes.exclude(status='A')
      context['classnotes_approved'] = classnotes.filter(status='A')
      context['classnotes_fellowship'] = classnotes.filter(status='F')
      context['classnotes_pending'] = classnotes.filter(status='P')
      context['classnotes_unsubmitted'] = classnotes.filter(status='U')
    elif user.type == 'T':
      context['classnotes_list'] = Classnotes.objects.all()
    return context


class ClassnotesReportView(ListView):
  template_name = 'classnotes/classnotes_report.html'
  model = Classnotes
  context_object_name = 'classnotes'

  # profile is the user that's currently logged in
  def get_context_data(self, **kwargs):
    context = super(ClassnotesReportView, self).get_context_data(**kwargs)
    week = self.request.GET.get('week', None)
    classnotes_unsubmitted = Classnotes.objects.filter(status__in=['F', 'U'])
    classnotes_unsubmitted = classnotes_unsubmitted.order_by('-trainee')
    if week is not None:
      term = Term.current_term()
      start = term.startdate_of_week(int(week))
      end = term.enddate_of_week(int(week))
      classnotes_unsubmitted = classnotes_unsubmitted.filter(date__gte=start, date__lte=end)
      context['for_week'] = str(week)
    context['classnotes_unsubmitted'] = classnotes_unsubmitted
    return context


class ClassnotesUpdateView(SuccessMessageMixin, UpdateView):
  '''
    View for trainee to edit class note
  '''
  model = Classnotes
  context_object_name = 'classnotes'
  template_name = 'classnotes/classnotes_detail.html'
  form_class = EditClassnotesForm
  success_url = reverse_lazy('classnotes:classnotes_list')
  success_message = "Classnotes Updated Successfully!"

  def get_context_data(self, **kwargs):
    context = super(ClassnotesUpdateView, self).get_context_data(**kwargs)
    context['profile'] = self.request.user
    context['audio'] = AudioFile.objects.get_file(self.get_object().event, self.get_object().date)
    return context

  def post(self, request, *args, **kwargs):
    pk = self.kwargs['pk']
    content = request.POST.get('content', '')
    classnotes = Classnotes.objects.get(pk=pk)
    classnotes.content = content
    if 'submit'in request.POST or 're_submit' in request.POST:
      classnotes.date_submitted = datetime.now()
      classnotes.status = 'P'
      messages.success(request, "Class notes submitted!")
      classnotes.save()
      return HttpResponseRedirect(reverse_lazy('classnotes:classnotes_list'))
    else:
      messages.success(request, "Class notes saved!")
      classnotes.save()
      return HttpResponseRedirect(reverse_lazy('classnotes:classnotes_detail', kwargs={'pk': pk}))


class ClassnotesApproveView(UpdateView):
  '''
    This view is for TA to approve selected class notes
  '''
  template_name = 'classnotes/classnotes_approve.html'
  form_class = ApproveClassnotesForm
  success_url = reverse_lazy('classnotes:classnotes_list')
  model = Classnotes
  context_object_name = 'classnotes'

  def get_context_data(self, **kwargs):
    # get curretn id, self.object
    ctx = super(ClassnotesApproveView, self).get_context_data(**kwargs)

    try:
      nxt = self.get_object().next()
      ctx['next_classnotes'] = nxt.id if nxt else -1
    except ValueError:
      ctx['next_classnotes'] = -1

    try:
      prev = self.get_object().prev()
      ctx['prev_classnotes'] = prev.id if prev else -1
    except ValueError:
      ctx['prev_classnotes'] = -1

    return ctx

  def post(self, request, *args, **kwargs):
    classnotes = self.get_object()
    url = post_classnotes(classnotes, request)
    return HttpResponseRedirect(url)


def post_classnotes(classnotes, request):
  comments = request.POST.get('comments', '')
  hard_copy = request.POST.get('submitting_paper_copy', False)
  classnotes.add_comments(comments)
  if hard_copy:
    classnotes.set_hard_copy(True)

  if 'fellowship' in request.POST:
    classnotes.set_fellowship()
    messages.success(request, "Marked for fellowship")
  if 'save' in request.POST:
    classnotes.save()
    messages.success(request, "TA comments updated")
    return reverse_lazy('classnotes:classnotes_approve', kwargs={'pk': classnotes.pk})
  if 'unfellowship' in request.POST:
    classnotes.remove_fellowship()
    messages.success(request, "Remove mark for fellowship")
  if 'approve' in request.POST:
    classnotes.approve()
    messages.success(request, "Class Notes Approved!")
  if 'hard_copy_approve' in request.POST:
    classnotes.hard_copy_approve()
    messages.success(request, "Checked Class notes(s) Hard-copy Approved!")
  if 'unapprove' in request.POST:
    classnotes.unapprove()
    messages.success(request, "Class Notes Un-Approved!")
  return reverse_lazy('classnotes:classnotes_list')


# Lock to TA
class ClassnotesAssignView(ListView):
  """
    This is where the TA's assign the Classnotes.
  """
  model = Trainee
  template_name = 'classnotes/assign_classnotes.html'
  context_object_name = 'trainees'

  def get_context_data(self, **kwargs):
    context = super(ClassnotesAssignView, self).get_context_data(**kwargs)
    term = Term.current_term()
    week = term.term_week_of_date(datetime.now().date())
    context['weekinit'] = str(week)
    context['week_range'] = [str(i) for i in range(20)]
    return context

  # this function is called whenever 'post'
  def post(self, request, *args, **kwargs):
    if all(params in request.POST for params in ['assign_classnotes', 'week']):
      week = int(request.POST['week'])
      assign_classnotes(week)
      messages.success(request, "Class notes assigned according to attendance!")
      return redirect(reverse_lazy('classnotes:classnotes_report') + '?week=' + str(week))
    return self.get(request, *args, **kwargs)


class ClassnotesCreateView(SuccessMessageMixin, CreateView):
  """
    From ClassnotesListView.
    gets: classname and classdate to display on form template
    post: classname, classdate, content
    Creates a new Classnotes object
  """

  model = Classnotes
  form_class = NewClassnotesForm
  success_url = reverse_lazy('classnotes:classnotes_list')
  success_message = "Class notes saved Successfully!"
  template_name = 'classnotes/classnotes_form.html'

  def get_initial(self):
    """
    Returns the initial data to use for forms on this view.
    """
    initial = super(ClassnotesCreateView, self).get_initial()
    initial['trainee'] = trainee_from_user(self.request.user)
    # initial['classname'] = classnotes.classname
    # initial['classdate'] = classnotes.classdate
    return initial

  def get_context_data(self, **kwargs):
    context = super(ClassnotesCreateView, self).get_context_data(**kwargs)
    # classnotes = Classnotes.objects.get(pk=self.kwargs['pk'])
    # context['classname'] = classnotes.classname
    # context['classdate'] = classnotes.classdate
    return context

  def form_valid(self, form):
    # classnotes = form.save(commit=False)

    classnotes = Classnotes.objects.get(pk=self.kwargs['pk'])
    # Check if minimum words are met
    if form.is_valid:
      # data = form.cleaned_data
      # classnotes.content = data['content']
      classnotes.date_submitted = datetime.now()
      classnotes.save()
    return super(ClassnotesCreateView, self).form_valid(form)


class ClassNoteViewSet(viewsets.ModelViewSet):
  queryset = Classnotes.objects.all()
  serializer_class = ClassnotesSerializer

  @detail_route(methods=['post'])
  def save_note(self, request, pk=None):
    instance = self.get_object()
    if instance.status == 'U':
      instance.content = request.data.get('content')
      instance.save()
      status = 'Saved at %s!' % time.strftime('%I:%M:%S %p')
    else:
      status = 'Class note is already submitted'
    return Response({'status': status})

  @detail_route(methods=['post'])
  def submit_note(self, request, pk=None):
    instance = self.get_object()
    if instance.status == 'U':
      instance.content = request.data.get('content')
      instance.status = 'P'
      instance.submitting_paper_copy = request.data.get('submitting_paper_copy') == 'true'
      instance.date_submitted = datetime.now()
      instance.save()
      status = 'Submitted at %s!' % time.strftime('%I:%M:%S %p')
    else:
      status = 'Class note is already submitted'
    return Response({'status': status})

  @detail_route(methods=['post'])
  def approve_note(self, request, pk=None):
    instance = self.get_object()
    if instance.status != 'A':
      instance.status = 'A'
      instance.TA_comment = request.data.get('TA_comment')
      instance.save()
      status = 'Approved!'
    else:
      status = 'Class note is already approved'
    return Response({'status': status})

  @detail_route(methods=['post'])
  def mark_note(self, request, pk=None):
    instance = self.get_object()
    if instance.status != 'F':
      instance.status = 'F'
      instance.TA_comment = request.data.get('TA_comment')
      instance.save()
      status = 'Marked for fellowship!'
    else:
      status = 'Class note is already marked for fellowship'
    return Response({'status': status})
