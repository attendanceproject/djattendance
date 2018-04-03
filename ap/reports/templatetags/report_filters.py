from django.template.defaulttags import register
import re
from decimal import *


@register.filter
def get_item(dict, index):
  return dict[list(dict.keys())[index]]

@register.filter
def get_item_for_dict(dict, item):
  return dict[item]

@register.filter
def get_date_range(dict):
	return dict['date_from'].strip('00:00:00') + ' to ' + dict['date_to'].strip('00:00:00')