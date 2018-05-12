from aputils.trainee_utils import is_trainee
from exams.utils import trainee_can_take_exam, makeup_available

from .models import Exam, Session


def exams_available(request):
  user = request.user
  if not hasattr(user, 'type') or not is_trainee(user):
    return {'exams_available': 0}

  exams = Exam.objects.filter(is_open=True)
  exam_count = 0
  for exam in exams:
    if trainee_can_take_exam(user, exam):
      exam_count += 1
  
  not_open_exams = Exam.objects.filter(is_open=False)
  for exam in not_open_exams:
    if makeup_available(exam, user):
      exam_count += 1

  return {'exams_available': exam_count}


def exams_taken(request):
  user = request.user
  if not hasattr(user, 'type') or not is_trainee(user):
    return {'exams_taken': 0}
  sessions = Session.objects.filter(trainee=user, is_graded=True)
  exam_count = 0
  for session in sessions:
    if session.exam == None:
      session.delete()
    elif session.exam.is_open:
      exam_count += 1
  exams_taken = exam_count > 0
  return {'exams_taken': exams_taken}
