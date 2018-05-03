from django.template.defaulttags import register
import re
from decimal import *


# for counter 1 return 1##2, for counter 2 return 3##4, for counter 3 return 5##6, for counter 4 return 7##8
@register.filter
def get_index_for_tf(index):
  return str(index + index - 1) + "##" + str(index * 2)


@register.filter
def get_answers(answers):
  return '; '.join(answer for answer in answers.split('##'))


@register.filter
def get_matching_answers(questions):
  return [str(answer) for answer in questions[0]['matching_answers']]


@register.filter
def get_answers(answers):
  return '; '.join(answer for answer in answers.split('##'))

@register.filter
def split_string_list(string):
  return string.split('##')


@register.filter
def split_string(string, delimiterIndex):
  delimiter = delimiterIndex.split(',')[0]
  index = int(delimiterIndex.split(',')[1])
  return string.split(delimiter)[index]


@register.filter
def get_letter_ordered_options(string):
  return sorted(string.split('##'))


@register.filter
def get_multiple_choice_option(string):
  return string[2:]


@register.filter
def get_fill_in_the_blank_string(string):
  blanks = re.findall(r'\$[0-9]+', string)
  rtn_str = string
  for each in blanks:

    rtn_str = rtn_str.replace(each, '_____(' + each[1] + ')_____')
  return rtn_str


@register.filter
def calculate_percentage(dividend, divisor):
  return (dividend / divisor * 100).quantize(Decimal('.01'), rounding=ROUND_UP)


@register.filter
def count_occurences_of_blanks(string):
  return re.findall('\$[0-9]+', string)


@register.filter
def get_blank_for_question(question, blank_index):
  return question.split('##')[blank_index]
