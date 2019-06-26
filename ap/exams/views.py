import json

from braces.views import LoginRequiredMixin, GroupRequiredMixin
from datetime import datetime

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Prefetch

from aputils.trainee_utils import trainee_from_user, is_TA
from aputils.utils import render_to_pdf
from aputils.decorators import group_required
from ap.forms import TraineeSelectForm
from terms.models import Term

from .forms import ExamCreateForm, ExamReportForm
from .models import Exam, Section, Session, Responses, Makeup
from .utils import get_exam_questions, save_exam_creation, get_exam_context_data, get_exam_preview_context_data, makeup_available, save_responses, trainee_can_take_exam, save_grader_scores_and_comments, is_float

from accounts.models import Trainee
from classes.models import Class

# PDF generation (Unused)
import cStringIO as StringIO
import xhtml2pdf.pisa as pisa
from cgi import escape


class ExamCreateView(LoginRequiredMixin, GroupRequiredMixin, FormView):

  template_name = 'exams/exam_form.html'
  form_class = ExamCreateForm
  success_url = reverse_lazy('exams:manage')
  group_required = [u'training_assistant']
  initial = {'term': Term.current_term()}

  def get_context_data(self, **kwargs):
    context = super(ExamCreateView, self).get_context_data(**kwargs)
    context['section_templates'] = dict(Section.SECTION_FORM_TEMPLATES)
    context['section_types'] = Section.SECTION_CHOICES
    return context

  def post(self, request, *args, **kwargs):
    # -1 value indicates exam is newly created
    success, message = save_exam_creation(request, None)
    return JsonResponse({'ok': success, 'msg': message})


class ExamEditView(ExamCreateView):

  def get_initial(self):
    exam = Exam.objects.get(pk=self.kwargs['pk'])
    return {'training_class': exam.training_class, 'term': exam.term, 'description': exam.description, 'duration': exam.duration}

  def get_success_url(self):
    return reverse_lazy('exams:edit', kwargs={'pk': self.kwargs['pk']})

  def get_preview_url(self):
    return reverse_lazy('exams:preview', kwargs={'pk': self.kwargs['pk']})

  def get_context_data(self, **kwargs):
    context = super(ExamEditView, self).get_context_data(**kwargs)
    exam = Exam.objects.get(pk=self.kwargs['pk'])
    context['exam_edit'] = True
    context['is_open'] = bool(exam.is_open)
    context['is_graded_open'] = bool(exam.is_graded_open)
    context['is_final'] = bool(exam.category == 'F')
    context['data'] = get_exam_questions(exam, True)
    context['total_score'] = exam.total_score
    return context

  def post(self, request, *args, **kwargs):
    pk = self.kwargs['pk']
    success, message = save_exam_creation(request, pk)
    return JsonResponse({'ok': success, 'msg': message})


class ExamDelete(GroupRequiredMixin, DeleteView, SuccessMessageMixin):
  model = Exam
  success_url = reverse_lazy('exams:manage')
  group_required = [u'training_assistant']
  success_message = "Exam was deleted."
  group_required = [u'exam_graders', u'training_assistant']


class ExamTemplateListView(ListView):
  template_name = 'exams/exam_template_list.html'
  model = Exam
  context_object_name = 'exams'

  def get_queryset(self):
    user = self.request.user
    is_manage = 'manage' in self.kwargs
    if is_manage:
      exams = Exam.objects.all()
    else:
      exams = []
      if user.type in ['R', 'C']:
        # Open exams
        if user.current_term == 1 or user.current_term == 2:
          for exam in Exam.objects.filter(is_open=True, is_graded_open=False):
            if exam.training_class.class_type == 'MAIN' or exam.training_class.class_type == '1YR' or exam.training_class.class_type == 'AFTN':
              exams.append(exam)
        elif user.current_term == 3 or user.current_term == 4:
          for exam in Exam.objects.filter(is_open=True, is_graded_open=False):
            if exam.training_class.class_type == 'MAIN' or exam.training_class.class_type == '2YR' or exam.training_class.class_type == 'AFTN':
              exams.append(exam)

        # Open graded exams
        sessions = Session.objects.filter(trainee=user, is_graded=True)
        for session in sessions:
          if session.exam is None:
            session.delete()
          elif session.exam.is_graded_open:
            exam = session.exam
            exam.visible = True
            exam.completed = True
            exam.graded = True
            exams.append(exam)

    makeup = Makeup.objects.filter(trainee=user)
    #all makeup exams should be open
    makeup_exams = []
    for makeup_exam in makeup:
      exams.append(makeup_exam.exam)
      makeup_exams.append(makeup_exam.exam)
    exams = list(reversed(exams))
    # TODO - Fix this. to show makeup
    for exam in exams:
      exam.visible = (exam.is_open and trainee_can_take_exam(user, exam)) or exam.is_graded_open
      if exam in makeup_exams:
        exam.visible = True
      # Don't show to exam service manage page
      if not is_manage and not exam.visible:
        exams.remove(exam)
        continue

      exam.completed = exam.has_trainee_completed(user)
      exam.graded = exam.is_exam_graded(user)

    return exams

  def get_context_data(self, **kwargs):
    ctx = super(ExamTemplateListView, self).get_context_data(**kwargs)
    user = self.request.user
    is_manage = 'manage' in self.kwargs
    ctx['exam_service'] = is_manage and user.is_designated_grader() or is_TA(user)
    ctx['classes'] = Class.regularclasses.all()
    ctx['terms'] = reversed(Term.objects.all())
    return ctx


class SingleExamGradesListView(GroupRequiredMixin, TemplateView):
  '''
    View for graders to enter scores for paper responses for a given exam.
  '''
  template_name = 'exams/single_exam_grades.html'
  group_required = [u'exam_graders', u'training_assistant']

  def get_context_data(self, **kwargs):
    context = super(SingleExamGradesListView, self).get_context_data(**kwargs)
    exam = Exam.objects.get(pk=self.kwargs['pk'])
    context['exam'] = exam

    trainees = Trainee.objects.all().order_by('lastname')

    #delete all sessions without exam or trainee
    (Session.objects.filter(trainee=None) | Session.objects.filter(exam=None)).delete()

    if exam.training_class.class_type == '1YR':
      trainees = trainees.filter(current_term__lte=2)
    elif exam.training_class.class_type == '2YR':
      trainees = trainees.filter(current_term__gte=3)

    trainees = trainees.prefetch_related('exam_sessions', Prefetch('exam_sessions', queryset=Session.objects.filter(exam=exam, time_finalized__isnull=False).order_by('-time_finalized'), to_attr='current_sessions')).prefetch_related('exam_makeup', Prefetch('exam_makeup', queryset=Makeup.objects.filter(exam=exam), to_attr='has_makeup'))

    context['data'] = trainees
    return context

  def post(self, request, *args, **kwargs):
    context = self.get_context_data()
    P = request.POST

    if 'delete-session-id' in P:
      session_id = int(P['delete-session-id'])
      Session.objects.filter(id=session_id).delete()
      messages.success(request, 'Exam deleted')

    elif 'unfinalize-session-id' in P:
      session_id = int(P['unfinalize-session-id'])
      try:
        session = Session.objects.get(id=session_id)
        session.is_graded = False
        session.save()

        if session.is_submitted_online:
          return HttpResponseRedirect(reverse_lazy('exams:grade', kwargs={'pk': session.id}))
      except Session.DoesNotExist:
        pass
    elif 'makeup-trainee-id' in P:
      trainee_id = int(P['makeup-trainee-id'])
      try:
        trainee = Trainee.objects.get(id=trainee_id)
        exam = Exam.objects.get(pk=self.kwargs['pk'])
        Makeup.objects.get_or_create(trainee=trainee, exam=exam)
        session, created = Session.objects.get_or_create(trainee=trainee, exam=exam)
        if not created:
          session.time_finalized = None
          session.is_graded = False
          session.save()
      except Trainee.DoesNotExist:
        pass
    elif 'close-makeup-trainee-id' in P:
      trainee_id = int(P['close-makeup-trainee-id'])
      try:
        trainee = Trainee.objects.get(id=trainee_id)
        exam = Exam.objects.get(pk=self.kwargs['pk'])
        makeup = Makeup.objects.filter(trainee=trainee, exam=exam)
        makeup.delete()
      except Trainee.DoesNotExist:
        pass
    else:
      exam = Exam.objects.get(pk=self.kwargs['pk'])

      grades = P.getlist('new-grade')
      trainee_ids = P.getlist('trainee-id')
      # trainees = Trainee.objects.filter(id__in=trainee_ids)
      trainees = Trainee.objects.filter(id__in=trainee_ids).prefetch_related('exam_sessions', Prefetch('exam_sessions', queryset=Session.objects.filter(exam=exam, time_finalized__isnull=False).order_by('-time_finalized'), to_attr='current_sessions'))
      # Reorder to id order
      trainees_tb = dict([(str(t.id), t) for t in trainees])
      trainees = [trainees_tb[id] if id in trainees_tb else None for id in trainee_ids]

      for index, trainee in enumerate(trainees):
        if trainee is None:
          continue
        if grades[index] == "":
          continue

        if not grades[index].isdigit() or not is_float(grades[index]):
          messages.add_message(request, messages.ERROR, 'Invalid input for trainee ' + str(trainee))
          continue

        sessions = trainee.current_sessions
        # Save grades for trainees who use paper submission
        session, created = Session.objects.update_or_create(
          exam=exam,
          trainee=trainee)
        session.is_submitted_online=False
        session.time_finalized=datetime.now()
        session.is_graded=True
        session.grade=float(grades[index])
        session.save()

      grades2 = P.getlist('session-id-grade')
      session_ids = P.getlist('session-id')
      sessions = Session.objects.filter(id__in=session_ids)
      sessions_tb = dict([(str(s.id), s) for s in sessions])
      sessions = [sessions_tb[id] if id in sessions_tb else None for id in session_ids]

      for index, session in enumerate(sessions):
        if session is None:
          continue
        grade = float(grades2[index]) if grades2[index].isdigit() or is_float(grades2[index]) else 0
        session.grade = grade
        session.is_graded = True
        session.save()
      messages.success(request, 'Exam grades saved.')

    return super(SingleExamGradesListView, self).render_to_response(context)


class GenerateGradeReports(GroupRequiredMixin, TemplateView):
  template_name = 'exams/exam_grade_reports.html'
  group_required = [u'exam_graders', u'training_assistant']

  def post(self, request, *args, **kwargs):
    context = self.get_context_data()
    return super(GenerateGradeReports, self).render_to_response(context)

  def get_context_data(self, **kwargs):
    ctx = super(GenerateGradeReports, self).get_context_data(**kwargs)
    pk = self.request.POST.get('exam')
    trainees = self.request.POST.getlist('trainee') if 'trainee' in self.request.POST else None
    initial = {}

    #delete all sessions without exam or trainee
    (Session.objects.filter(trainee=None) | Session.objects.filter(exam=None)).delete()

    if pk:
      sessions = Session.objects.filter(exam__pk=pk)
      initial['exam'] = pk
    else:
      # Get all the exams
      sessions = Session.objects.all()

    ctx['sessions'] = sessions.prefetch_related('exam', 'trainee').order_by('trainee__lastname')
    if trainees:
      ctx['sessions'] = sessions.filter(trainee__in=trainees)
      initial['trainee'] = [int(t) for t in trainees]

    ctx['trainee_select_form'] = TraineeSelectForm()
    ctx['trainee_select_field'] = ExamReportForm(initial=initial)

    return ctx


class GenerateOverview(GroupRequiredMixin, TemplateView):
  template_name = 'exams/exam_overview.html'
  group_required = [u'exam_graders', u'training_assistant']

  def get_context_data(self, **kwargs):
    context = super(GenerateOverview, self).get_context_data(**kwargs)
    exam = Exam.objects.get(pk=self.kwargs['pk'])
    context['exam'] = exam
    context.update(exam.statistics())

    #delete all sessions without exam or trainee
    (Session.objects.filter(trainee=None) | Session.objects.filter(exam=None)).delete()

    try:
      context['sessions'] = Session.objects.filter(exam=exam).order_by('trainee__lastname')
    except Session.DoesNotExist:
      context['sessions'] = []
    return context


class ExamMakeupView(GroupRequiredMixin, ListView):
  '''
    Prints PDF of list of trainees that has makeup option open
    TODO - Move this part to reports
  '''
  model = Makeup
  template_name = 'exams/exam_makeup_list.html'
  context_object_name = 'makeup_list'
  group_required = [u'exam_graders', u'training_assistant']

  def get_queryset(self):
    if 'pk' in self.kwargs:
      exam = Exam.objects.filter(pk=self.kwargs['pk']).first()
      return Makeup.objects.filter(exam=exam)
    return Makeup.objects.all()

  def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    context = super(ExamMakeupView, self).get_context_data(**kwargs)
    return render_to_pdf(
      'exams/exam_retake_list.html',
      context
    )


class PreviewExamView(GroupRequiredMixin, SuccessMessageMixin, ListView):
  template_name = 'exams/exam.html'
  model = Session
  context_object_name = 'exam'
  fields = []
  group_required = [u'training_assistant']

  def _get_exam(self):
    return Exam.objects.get(pk=self.kwargs['pk'])

  def _exam_available(self):
    return True

  def get_context_data(self, **kwargs):
    context = super(PreviewExamView, self).get_context_data(**kwargs)
    return get_exam_preview_context_data(context, self._get_exam())


class TakeExamView(SuccessMessageMixin, CreateView):
  template_name = 'exams/exam.html'
  model = Session
  context_object_name = 'exam'
  fields = []

  def get_success_url(self):
    return reverse_lazy('exams:list')

  def _get_exam(self):
    return Exam.objects.get(pk=self.kwargs['pk'])

  def _get_most_recent_session(self):
    return Session.objects.filter(exam=self._get_exam(), trainee=self.request.user).order_by('-time_started').first()

  def _get_session(self):
    if not self._exam_available():
      return None

    session = self._get_most_recent_session()
    # Create a new exam session if there is no editable exam session
    # TODO - Check if now - time_started is greater than exam.duration
    if session is None:
      session = Session(
          trainee=trainee_from_user(self.request.user),
          exam=self._get_exam(),
          is_submitted_online=True)
      session.save()

    return session

  def _exam_available(self):
    return True
    exam = self._get_exam()
    user = self.request.user

    if not trainee_can_take_exam(user, exam):
      return False

    # if the exam is in progress or doesn't exist, we're in business
    most_recent_session = self._get_most_recent_session()

    if (most_recent_session is None):
      return True

    return makeup_available(exam, user)

  def get_context_data(self, **kwargs):
    context = super(TakeExamView, self).get_context_data(**kwargs)
    return get_exam_context_data(
        context,
        self._get_exam(),
        self._exam_available(),
        self._get_session(),
        "Take",
        False)

  def post(self, request, *args, **kwargs):
    is_successful = True
    finalize = False
    is_graded = False
    session = self._get_session()

    try:
      body_unicode = request.body.decode('utf-8')
      body = json.loads(body_unicode)
    except ValueError:
      message = "Something went wrong. Try again."
      return JsonResponse({'bad': False, 'finalize': finalize, 'msg': message})

    for k, v in body.items():
      if k == "Submit":
        if v == 'true':
          finalize = True
      else:
        section = Section.objects.filter(id=int(k)).first()
        if section:
          save_responses(session, section, v)
        else:
          is_successful = False

    # Do automatic scoring if trainee finalize exam
    total_session_score = 0
    if finalize and is_successful:
      # remove this for now per Raizel's request; what this does is it only considers this exam graded if no essay questions
      # is_graded = not session.exam.sections.filter(section_type='E').exists()
      responses = Responses.objects.filter(session=session)

      # Code to check if number of responses in section is equal or greater than number of responses needed to submit in section
      num_responses_in_section = 0
      for response in responses:

        for each_answer in response.responses:
          if response.responses[each_answer].replace("##", "") != '""':
            num_responses_in_section += 1
        if num_responses_in_section < response.section.required_number_to_submit:
          message = "Number of responses in section does not reach minimum amount of responses required."
          return JsonResponse({'bad': False, 'finalize': finalize, 'msg': message})
      for resp_obj_to_grade in responses:
        section = resp_obj_to_grade.section
        total_session_score += section.autograde(resp_obj_to_grade)
    message = 'Exam submitted successfully.'
    if finalize:
      session = self._get_session()
      if session.exam.is_open:
        session.time_finalized = datetime.now()
        session.grade = total_session_score
        session.is_graded = is_graded
        session.save()
      else:
        finalize = False
        message = 'Cannot finalize because exam is closed. Exam progress saved.'
        return JsonResponse({'bad': False, 'finalize': finalize, 'msg': message})
    else:
      message = 'Exam progress saved.'

    return JsonResponse({'ok': is_successful, 'finalize': finalize, 'msg': message})


class GradeExamView(GroupRequiredMixin, CreateView):
  template_name = 'exams/exam.html'
  model = Session
  context_object_name = 'exam'
  fields = []
  group_required = [u'exam_graders', u'training_assistant']

  def get_success_url(self):
    session = Session.objects.get(pk=self.kwargs['pk'])
    return reverse_lazy('exams:grades', kwargs={'pk': session.exam.id})

  def _get_exam(self):
    session = Session.objects.get(pk=self.kwargs['pk'])
    return Exam.objects.get(pk=session.exam.id)

  def _get_session(self):
    return Session.objects.get(pk=self.kwargs['pk'])

  def _exam_available(self):
    # TODO: should sanity check that user has grader/TA permissions
    return True

  def get_context_data(self, **kwargs):
    context = super(GradeExamView, self).get_context_data(**kwargs)
    return get_exam_context_data(
        context,
        self._get_exam(),
        self._exam_available(),
        self._get_session(),
        "Grade", True)

  # Returns true if every score has a valid value
  def calculate_score(self, request, responses, session, section):
    total_score = 0
    can_finalize = True
    for index, response in enumerate(responses):
      response_parsed = response
      if response_parsed["score"].isdigit() or is_float(response_parsed["score"]):
        total_score += float(response_parsed["score"])
      else:
        can_finalize = False
        if response_parsed["score"] != "":
          messages.add_message(request, messages.ERROR, "Invalid grade value for question" + str(index + 1) + ".")

    try:
      responses_obj = Responses.objects.get(session=session, section=section)
    except Responses.DoesNotExist:
      responses_obj = Responses(session=session, section=section, score=0)

    if (responses_obj.score != total_score):
      session.grade = session.grade - responses_obj.score + total_score
      session.save()

      responses_obj.score = total_score
      responses_obj.save()

    return can_finalize

  def post(self, request, *args, **kwargs):
    is_successful = True
    finalize = False
    if 'Submit' in request.POST:
      finalize = True

    session = Session.objects.get(pk=self.kwargs['pk'])
    exam = Exam.objects.get(pk=session.exam.id)

    try:
      body_unicode = request.body.decode('utf-8')
      body = json.loads(body_unicode)
    except ValueError:
      body = []

    P = request.POST
    scores = P.getlist('section-score')
    comments = P.getlist('grader-comment')
    responses = session.responses.all()
    resp_s = {}
    total_score = 0
    index = 0
    for each in responses:
      try:
        section = Section.objects.get(exam=exam, section_index=index)
      except Section.DoesNotExist:
        is_successful = False
      resp_s['score'] = scores[index]
      if not resp_s['score'].isdigit() or not is_float(resp_s['score']):
        messages.add_message(request, messages.ERROR, 'Invalid score')
      resp_s['comments'] = comments[index]
      index += 1
      save_grader_scores_and_comments(session, section, resp_s)
      total_score += float(resp_s['score'])

    session.grade = total_score
    session.save()

    if finalize:
      session = self._get_session()
      session.is_graded = True
      session.save()
      messages.success(request, 'Exam grading submitted successfully.')
      return HttpResponseRedirect(reverse_lazy('exams:grades', kwargs={'pk': exam.id}))
    else:
      messages.success(request, 'Exam grading progress saved.')
      return self.get(request, *args, **kwargs)


class GradedExamView(TakeExamView):
  template_name = 'exams/exam_graded.html'

  #not really needed, as this is checked again in get_exam_context_data in utils.py
  def _exam_available_to_see(self):
    if self._get_exam().is_graded_open and self._get_session().is_graded and self._get_session().time_finalized != None:
      return True
    else:
      return False

  def get_context_data(self, **kwargs):
    context = super(GradedExamView, self).get_context_data(**kwargs)
    ctx = get_exam_context_data(
        context,
        self._get_exam(),
        self._exam_available_to_see(),
        self._get_session(),
        "View", True)
    ctx['graded_exam_available'] = self._get_exam().is_graded_open
    return ctx

class OpenCloseExamView(ExamEditView):
  def post(self, request, *args, **kwargs):

    if request.method=="POST":
      try:
        pk = int(request.POST['exam_id'])

        exam = Exam.objects.get(id=pk)
        exam.is_open = not exam.is_open
        exam.save()
      except KeyError:
        return HttpResponse('Error')
      return HttpResponseRedirect(reverse_lazy('exams:manage'))
    else:
      raise Http404