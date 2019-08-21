from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin

from .utils import unfinalized_week


class BibleReadingMiddleware(MiddlewareMixin):
  def process_request(self, request):
    url_list = [reverse('bible_tracker:index'), reverse('login'), reverse('logout')]
    exception_list = [
        reverse('bible_tracker:changeWeek'), reverse('bible_tracker:updateStatus'),
        reverse('bible_tracker:finalizeStatus'), reverse('bible_tracker:updateBooks'),
        reverse('apimport:term_details'), reverse('apimport:process_csv'), reverse('apimport:save_data')
    ]
    if request.path in exception_list or settings.DEBUG:
      return None
    if request.path not in url_list:
      week = unfinalized_week(request.user)
      if week and not settings.DEBUG:
        return None
        #return HttpResponseRedirect(reverse('bible_tracker:index') + '?week=' + str(week))
    return None
