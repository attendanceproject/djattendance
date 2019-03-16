from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin

from .utils import unfinalized_service


class DesignatedServiceHoursMiddleware(MiddlewareMixin):
  @classmethod
  def process_request(self, request):
    url_list = [
        reverse('services:designated_service_hours'), reverse('login'),
        reverse('logout'), reverse('bible_tracker:index')
    ]
    exception_list = [
        reverse('bible_tracker:changeWeek'), reverse('bible_tracker:updateStatus'),
        reverse('bible_tracker:finalizeStatus'), reverse('bible_tracker:updateBooks'),
        reverse('apimport:term_details'), reverse('apimport:process_csv'), reverse('apimport:save_data')
    ]
    if (request.path in exception_list or "/services/designated_service_hours" in request.path or settings.DEBUG):
      return None
    if request.path not in url_list:
      unfinalizedService = unfinalized_service(request.user)
      if unfinalizedService and not settings.DEBUG:
        return HttpResponseRedirect(
            reverse('services:designated_service_hours') + '/' + str(unfinalizedService[0]) + '/' + str(unfinalizedService[1])
        )
    return None
