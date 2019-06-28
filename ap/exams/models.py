import ast
from decimal import Decimal

from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.utils.timezone import timedelta

from accounts.models import Trainee
from classes.models import Class
from terms.models import Term

""" exams models.py

This module allows for administering and taking of exams, including exam
creation, editing, taking, grading, and retaking functionalities.  This module
does not handle determining class grades or generation of retake lists.

DATA MODELS:
  - Exam: Describes an exam or assessment that a trainee can take on the
    server.  This is not used for assessments only available offline.
  - Section: describes a section of an exam.  Includes instructions and
    the questions for the section.
  - Session: a specific instance of an exam, holds general information
    pertaining to this take of the exam (e.g. trainee taking the exam
    and completion statuses).
  - Responses: Holds a trainee's response to a particular section on the exam
    as well as information related to the grade or grading of the section.
  - Makeup: List of Trainee/Exam pairs that indicates which combinations
    are valid for makeup.
"""


class Exam(models.Model):
  training_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
  description = models.CharField(max_length=250, blank=True)
  is_open = models.BooleanField(default=False)
  is_graded_open = models.BooleanField(default=False)
  term = models.ForeignKey(Term, null=True, on_delete=models.SET_NULL)
  duration = models.DurationField(default=timedelta(minutes=90))

  # does this exam contribute to the midterm grade or to the final grade?
  CATEGORY_CHOICES = (('M', 'Midterm'),
                      ('F', 'Final'))
  category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)

  # total score is not user set--this is set as questions are added and point
  # values assigned for each question.
  total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, editable=False)

  # passing_percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

  def __unicode__(self):
    try:
      return "%s [%s] - %s" % (self.get_category_display(), self.term, self.training_class.name)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  # an exam is available to a particular trainee if the trainee is registered
  # for the class related to the exam and either the exam is (open and not
  # completed by the trainee) or (trainee is on the retake list for this exam)
  def is_available(self, trainee):
    # TODO: is the trainee registered for this class?
    if Makeup.objects.filter(exam=self, trainee=trainee).exists():
      return True
    if not self.is_open:
      return False
    if Session.objects.filter(exam=self, trainee=trainee, time_finalized__isnull=True).exists():
      return True
    return False

  def has_trainee_completed(self, trainee):
    return Session.objects.filter(exam=self, trainee=trainee, time_finalized__isnull=False).exists()

  def is_exam_graded(self, trainee):
    return Session.objects.filter(exam=self, trainee=trainee, is_graded=True).exists()

  def statistics(self):

    exams = Session.objects.filter(exam=self, is_graded=True)
    total = Decimal(0.0)
    count = Decimal(0.0)

    minimum = self.total_score
    maximum = Decimal(0.0)
    stats = {'maximum': 'n/a', 'minimum': 'n/a', 'average': 'n/a'}
    for exam in exams:
      total = total + exam.grade
      count = count + 1
      if exam.grade <= minimum:
        stats['minimum'] = exam.grade
        minimum = exam.grade
      if exam.grade >= maximum:
        stats['maximum'] = exam.grade
        maximum = exam.grade
    if count > 0:
      stats['average'] = total / count
    return stats

  def _section_count(self):
    return self.sections.count()
  section_count = property(_section_count)


class Section(models.Model):
  exam = models.ForeignKey(Exam, related_name='sections', null=False)
  SECTION_CHOICES = (('MC', 'Multiple Choice'),
                     ('E', 'Essay'),
                     ('M', 'Matching'),
                     ('TF', 'True False'),
                     ('FB', 'Fill in the Blank'))
  section_type = models.CharField(max_length=2, choices=SECTION_CHOICES, default='E')

  SECTION_TEMPLATES = (
      ('E', 'exams/essay_question_template.html'),
      ('MC', 'exams/mc_question_template.html'),
      ('M', 'exams/matching_question_template.html'),
      ('TF', 'exams/tf_question_template.html'),
      ('FB', 'exams/fitb_question_template.html'),
  )

  SECTION_FORM_TEMPLATES = (
      ('E', 'exams/essay_question.html'),
      ('M', 'exams/matching_question.html'),
      ('TF', 'exams/tf_question.html'),
      ('FB', 'exams/fitb_question.html'),
      ('MC', 'exams/mc_question.html'),
  )

  @property
  def question_template(self):
    return dict(Section.SECTION_TEMPLATES)[self.section_type]

  # Instructions
  instructions = models.TextField(null=True, blank=True)

  # Required number of questions needed to submit exam
  required_number_to_submit = models.IntegerField(default=0)

  # First section in exam has a section_index of 0
  section_index = models.IntegerField(default=0)

  first_question_index = models.IntegerField(default=1)
  question_count = models.IntegerField()
  questions = HStoreField(null=True)

  def __unicode__(self):
    try:
      return "Section %s [%s] for %s" % (self.section_index, self.get_section_type_display(), self.exam)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  class Meta:
    ordering = ['exam', 'section_index']
    unique_together = ('exam', 'section_index')

  def autograde(self, response):
    if self.section_type != 'E':
      responses = response.responses
      score_for_section = 0
      for i in range(1, self.question_count + 1):
        question_data = ast.literal_eval(self.questions[str(i)])
        # see if response of trainee equals answer; if it does assign point
        if self.section_type == 'FB':
          responses_to_blanks = responses[str(i)].replace('\"', '').lower().split('$')
          answers_to_blanks = str(question_data["answer"]).lower().split('$')
          total_blanks = len(responses_to_blanks)
          number_correct = 0
          for i in range(0, total_blanks):
            try:
              if responses_to_blanks[i] == answers_to_blanks[i]:
                number_correct += 1
            except IndexError:
              continue
          # TODO: convert to decimal
          blank_weight = float(question_data["points"]) / float(total_blanks)
          score_for_section += (number_correct * blank_weight)
        # Everything else other than FB and Essay can be automatically graded with this
        elif (responses[str(i)].replace('\"', '').lower() == str(question_data["answer"]).lower()):
          score_for_section += int(question_data["points"])
      response.score = score_for_section
    else:
      response.comments = "NOT GRADED YET"
    # Finally save the response
    response.save()
    return response.score if response.score else 0


class Session(models.Model):

  trainee = models.ForeignKey(Trainee, related_name='exam_sessions', null=False)
  exam = models.ForeignKey(Exam, related_name='sessions', null=False)

  is_submitted_online = models.BooleanField(default=True)
  is_graded = models.BooleanField(default=False)
  time_started = models.DateTimeField(auto_now_add=True, null=True, blank=True)
  time_finalized = models.DateTimeField(null=True, blank=True)

  # Calculated and set when grader saves/finalizes exam grading or, if not
  # taken online, set by the grading sister manually.
  grade = models.DecimalField(max_digits=5, decimal_places=2, default=0)

  def __unicode__(self):
    try:
      return "%s for %s" % (self.exam, self.trainee)
    except AttributeError as e:
      return str(self.id) + ": " + str(e)

  class Meta:
    ordering = ['trainee']
    unique_together = ('trainee', 'exam')


class Responses(models.Model):
  session = models.ForeignKey(Session, related_name='responses', null=False)
  section = models.ForeignKey(Section, related_name='responses', null=False)

  responses = HStoreField(null=True)
  score = models.DecimalField(max_digits=5, decimal_places=2)
  comments = models.TextField(null=True, blank=True)

  class Meta:
    verbose_name = "response"
    unique_together = ('session', 'section')


# Makeup are deleted upon creation of session.
class Makeup(models.Model):
  trainee = models.ForeignKey(Trainee, related_name='exam_makeup', null=False)
  exam = models.ForeignKey(Exam, null=False)
  time_opened = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = ('trainee', 'exam')
