from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from django.core.urlresolvers import reverse
from .utils import unfinalized_week


class BibleReadingMiddleware(MiddlewareMixin):
  def process_request(self, request):
    url_list = [reverse('bible_tracker:index'), reverse('login'), reverse('logout')]
    exception_list = [
        reverse('bible_tracker:changeWeek'), reverse('bible_tracker:updateStatus'),
        reverse('bible_tracker:finalizeStatus'), reverse('bible_tracker:updateBooks')
    ]
    if request.path in exception_list:
      return None
    if request.path not in url_list:
      week = unfinalized_week(request.user)
      if week:
        return HttpResponseRedirect(reverse('bible_tracker:index') + '?week=' + str(week))
    return None
