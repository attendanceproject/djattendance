import json
import random
import re
import ast

from django.template.defaulttags import register

from .models import Exam, Makeup, Responses, Section


@register.filter
def get_letter_for_multiple_choice_index(index):
    return chr(64+int(index))


# Returns the section referred to by the args, None if it does not exist
def get_exam_section(exam, section_id):
  return Section.objects.filter(exam=exam, section_index=section_id).first()


# Returns an array containing the interesting data for the given section.
# Return None if exam is invalid
def get_exam_questions_for_section(exam, section_id, include_answers):
  section = get_exam_section(exam, section_id)
  section_obj = {}
  questions = []

  if section is None:
    return None

  for i in range(section.first_question_index, section.question_count + 1):
    q = section.questions[str(i)]
    questions.append(json.loads(q))
  section_obj['type'] = section.section_type
  section_obj['section_type'] = section.get_section_type_display()
  section_obj['instructions'] = section.instructions
  section_obj['required_number_to_submit'] = section.required_number_to_submit
  section_obj['template'] = section.question_template
  section_obj['id'] = section.id
  section_obj['questions'] = questions
  matching_answers = []
  if not include_answers:
    for each in section_obj['questions']:
      answer = each.pop('answer', None)
      if section_obj['type'] == 'M' and answer is not None and answer not in matching_answers:
        matching_answers.append(answer)
  random.shuffle(matching_answers)
  if matching_answers != []:
    section_obj['matching_answers'] = matching_answers
  return section_obj


# Returns an array containing the interesting data.  None is returned if the
# exam is invalid.
def get_exam_questions(exam, include_answers):
  sections = []
  for i in range(0, exam.section_count):
    section_questions = get_exam_questions_for_section(exam, i, include_answers)
    if (section_questions is not None):
      sections.append(section_questions)
    else:
      return []

    # TODO(verification): We should sanity check that the question numbers
    # per section are vaguely correct whenever we have an exam that has
    # when we start having exams with more than one section.
  return sections


# Returns a tuple of responses, grader_extras, and scores for the given exam
# in the given section
def get_responses_for_section(exam_pk, section_index, session):
  section = get_exam_section(exam_pk, section_index)
  responses = {}
  if section is None:
    return []

  try:
    responses_object = Responses.objects.get(session=session, section=section)
  except Responses.DoesNotExist:
    responses_object = None

  for i in range(section.first_question_index, section.question_count + 1):
    if responses_object and str(i) in responses_object.responses:
      r = responses_object.responses[str(i)]
      responses[i] = json.loads(r)
    else:
      if section.section_type == 'FB':
        regex = re.compile('[^##]')
        responses[i] = json.loads('"' + regex.sub('', section.questions[str(i)]) + '"')
      else:
        responses[i] = json.loads('""')
      # responses[i] = {}
  return responses


# Returns a tuple of responses, grader_extras, and scores for the given exam
def get_responses(exam, session):
  responses = []
  sections = Section.objects.filter(exam=exam)

  for i in range(0, len(sections)):
    responses.append(get_responses_for_section(exam, i, session))
  return responses


def get_responses_score_for_section(exam_pk, section_index, session):
  section = get_exam_section(exam_pk, section_index)
  responses = {}
  if section is None:
    return []
  try:
    responses_object = Responses.objects.get(session=session, section=section)
  except Responses.DoesNotExist:
    responses_object = None
  for i in range(section.first_question_index, section.question_count + 1):
    if responses_object and str(i) in responses_object.responses:
      section_score = responses_object.score
      responses[i] = json.loads('"' + str(section_score) + '"')
  return responses


# data context format is: [({'type': u'essay', 'id': 102, 'questions': [...], 'instructions': u'write an essay'}, {0: u'I think it was okay'}), ...]
def get_responses_score(exam, session):
  responses_score = []
  sections = Section.objects.filter(exam=exam)
  for i in range(0, len(sections)):
    responses_score.append(get_responses_score_for_section(exam, i, session))
  return responses_score


def get_responses_comments_for_section(exam_pk, section_index, session):
  section = get_exam_section(exam_pk, section_index)
  responses = {}
  if section is None:
    return []
  try:
    responses_object = Responses.objects.get(session=session, section=section)
  except Responses.DoesNotExist:
    responses_object = None
  for i in range(section.first_question_index, section.question_count + 1):
    if responses_object and str(i) in responses_object.responses:
      section_comments = responses_object.comments
      responses[i] = json.loads('"' + str(section_comments) + '"')
  return responses


def get_responses_comments(exam, session):
  responses_comments = []
  sections = Section.objects.filter(exam=exam)
  for i in range(0, len(sections)):
    responses_comments.append(get_responses_comments_for_section(exam, i, session))
  return responses_comments


# if exam is new, pk will be a negative value
def save_exam_creation(request, pk):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  # METADATA
  mdata = body['metadata']
  # Sanity check
  training_class = mdata.get('training_class', None)
  term = mdata.get('term', None)
  exam_category = mdata.get('exam_category', None)
  # Throw error if none of these are specified
  if None in (training_class, term, exam_category):
    return (False, 'Invalid exam data.')  # TODO - Come up with better copy for this error message

  # Provide defaults for not important stuff
  exam_description = mdata.get('description', '')
  if exam_description == "":
    return (False, "No exam description given.")
  is_open = mdata.get('is_open', False)
  duration = mdata.get('duration', 90)
  if not is_float(duration):
    duration_regex = re.match('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$', duration)
    try:
      #okay match to regex pattern hh:mm:ss
      duration_regex.group(0)
    except AttributeError :
      return (False, 'Invalid duration given for exam.')


  total_score = mdata.get('exam-total-point', '')
  if total_score == '':
    return (False, "No exam total score given.")

  exam, created = Exam.objects.get_or_create(pk=pk, defaults={'training_class_id': training_class})
  exam.training_class_id = training_class
  exam.term_id = term
  exam.description = exam_description
  exam.is_open = is_open
  exam.duration = duration
  exam.category = exam_category
  exam.total_score = total_score
  existing_sections = map(lambda s: int(s.id), exam.sections.all())

  # SECTIONS
  sections = body['sections']
  section_index = 0
  for section in sections:
    section_id = int(section.get('section_id', -1))
    section_instructions = section['instructions']
    if section_instructions == "":
      exam.delete()
      for section in Section.objects.all():
        if section.exam == None:
          section.delete()
      return (False, "No section instructions given.")
    section_questions = section['questions']
    section_type = section['section_type']
    required_number_to_submit = section['required_number_to_submit']
    question_hstore = {}
    question_count = 1
    matching_answers = set()
    # Start packing questions
    for question in section_questions:
      # Avoid saving hidden questions that are blank
      if question['question-prompt'] == '':
        if section_type == "M" and question["question-match"] != '':
          matching_answers.add(question["question-match"])
          continue
        else:
          exam.delete()
          for section in Section.objects.all():
            if section.exam == None:
              section.delete()
          return (False, "No prompt given for question.")
      qPack = {}
      try:
        question_point = float(question['question-point'])
      except ValueError:
        if section_type == "M" and question["question-match"] != '':
          matching_answers.add(question["question-match"])
          continue
        else:
          exam.delete()
          for section in Section.objects.all():
            if section.exam == None:
              section.delete()
          return (False, "No point value for question given.")
      qPack['prompt'] = question['question-prompt']
      qPack['points'] = question_point
      #total_score += question_point
      options = ""
      answer = ""
      if section_type == "MC":
        for k, v in question.items():
          if 'question-option-' in k:
            question_letter = k.strip('question-option-')
            options += question_letter + "-" + v + "##"
            if question_letter in question:
              # every checked choice i.e. the answer to the question will go here
              answer += question_letter + "-" + v + "##"
        options = options.rstrip('##')
        qPack['options'] = options
        answer = answer.rstrip('##')
        qPack['question_number'] = question_count
      elif section_type == "M":
        answer = question["question-match"]
        matching_answers.add(question["question-match"])
      elif section_type == "TF":
        answer = question["answer"]
      elif section_type == "FB":
        for k, v in sorted(question.items()):
          if 'answer-text-' in k:
            answer += v + "##"
      answer = answer.rstrip('##')
      qPack['answer'] = answer
      question_hstore[str(question_count)] = json.dumps(qPack)
      question_count += 1

    # Either save over existing Section or create new one
    if section_id in existing_sections:
      section_obj = Section.objects.get(pk=section_id)
      existing_sections.remove(section_id)
    else:
      section_obj = Section(exam=exam)
    section_obj.instructions = section_instructions
    section_obj.section_type = section_type
    section_obj.section_index = section_index
    try:
      section_obj.required_number_to_submit = float(required_number_to_submit)
    except ValueError:
      exam.delete()
      for section in Section.objects.all():
        if section.exam == None:
          section.delete()
      return (False, "No 'required number of questions to answer for section' given.")
    if section_obj.section_type == "M":
      #append all possible matching answers
      for question_index in question_hstore:
        question_to_append_matching_answers = ast.literal_eval(question_hstore[str(question_index)])
        question_to_append_matching_answers['matching_answers'] = list(matching_answers)
        question_hstore[str(question_index)] = json.dumps(question_to_append_matching_answers).decode('utf-8')

    section_obj.questions = question_hstore
    section_obj.question_count = len(section_obj.questions)
    section_index += 1

    section_obj.save()

  # Delete old sections that are not touched
  for remaining_id in existing_sections:
    Section.objects.filter(id=remaining_id).delete()

  # Update total score
  #exam.total_score = total_score
  exam.save()

  # We made it!
  return (True, 'Exam Saved')


def get_exam_context_data(context, exam, is_available, session, role, include_answers):
  context['role'] = role
  context['exam'] = exam
  context['exam_total_score'] = exam.total_score
  if hasattr(session, 'trainee'):
    context['examinee'] = session.trainee
    context['examinee_score'] = session.grade
  if not is_available:
    context['exam_available'] = False
    return context
  context['is_graded'] = session.is_graded
  if session.time_finalized != None and exam.is_open and session.is_graded:
    context['exam_available'] = True
  elif session.time_finalized != None or not exam.is_open:
    context['exam_available'] = False
  else:
    context['exam_available'] = True
  #check if exam is available
  if hasattr(session, 'trainee') and not exam.is_open:
    context['exam_available'] = makeup_available(exam, session.trainee)
  questions = get_exam_questions(exam, include_answers)
  responses = get_responses(exam, session)
  score_for_responses = get_responses_score(exam, session)
  comments_for_responses = get_responses_comments(exam, session)

  context['data'] = zip(questions, responses, score_for_responses, comments_for_responses)

  return context


def makeup_available(exam, trainee):
  return Makeup.objects.filter(exam=exam, trainee=trainee).exists()


def save_responses(session, section, responses):
  try:
    responses_obj = Responses.objects.get(session=session, section=section)
  except Responses.DoesNotExist:
    responses_obj = Responses(session=session, section=section, score=0)
  responses_hstore = responses_obj.responses
  if responses_hstore is None:
    responses_hstore = {}

  # NEW CODE TO TAKE CARE OF BLANK ANSWERS
  for i in range(1, section.question_count + 1):
    try:
      responses_hstore[str(i).decode('utf-8')] = json.dumps(responses[str(i)])
    except KeyError:
      responses_hstore[str(i).decode('utf-8')] = json.dumps(str('').decode('utf-8'))

  responses_obj.responses = responses_hstore
  responses_obj.save()


def save_grader_scores_and_comments(session, section, responses):
  responses_obj, created = Responses.objects.get_or_create(session=session, section=section, defaults={'score': 0})
  responses_obj.score = responses['score']
  if section.section_type == 'E' and responses['comments'] == "NOT GRADED YET":
    responses_obj.comments = "GRADED"
  else:
    responses_obj.comments = responses['comments']
  responses_obj.save()


def trainee_can_take_exam(trainee, exam):
  if exam.training_class.class_type == 'MAIN':
    return trainee.is_active
  elif exam.training_class.class_type == '1YR':
    return trainee.current_term <= 2
  elif exam.training_class.class_type == '2YR':
    return trainee.current_term >= 3
  else:
    # fix when pushing
    return trainee.is_active
    # return False  #NYI


def is_float(value):
  try:
    float(value)
    return True
  except ValueError:
    return False
