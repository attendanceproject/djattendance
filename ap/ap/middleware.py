import re

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

# TODO: we need to fix how our authorization works
WEB_ACCESS_EX = [reverse('web_access:get-remote-address'), reverse('web_access:get-guest-requests'), reverse('web_access:create-guest-request'), reverse('web_access:delete-guest-request')]
IMPORT_EX = [reverse('apimport:process_csv'), reverse('apimport:term_details'), reverse('apimport:save_data')]
ROOM_EX = [reverse('room_reservations:room-reservation-tv-page'), reverse('room_reservations:tv-page-reservations'), reverse('room_reservations:weather'), reverse('room_reservations:tv-page-ticker'), 'room_reservations:tv-page-version']
EXEMPT_URLS = [reverse('login'), reverse('logout'), reverse('home')] + WEB_ACCESS_EX + IMPORT_EX + ROOM_EX

EXEMPT_REGEX = [re.compile(r'^/web_access/start-access/(?P<id>\d+)$'),
                re.compile(r'^/web_access/delete/(?P<pk>\d+)$'),
                re.compile(r'^/web_access/update/(?P<pk>\d+)$')]


class LoginRequiredMiddleware(MiddlewareMixin):  # http://onecreativeblog.com/post/59051248/django-login-required-middleware
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """
    def process_request(self, request):
      assert hasattr(request, 'user'), "The Login Required middleware\
          requires authentication middleware to be installed. Edit your\
          MIDDLEWARE_CLASSES setting to insert\
          'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
          work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
         'django.core.context_processors.auth'."

      if not request.user.is_authenticated:
        if request.path not in EXEMPT_URLS and not any(regex.match(request.path) for regex in EXEMPT_REGEX):
          return HttpResponseRedirect(reverse('login'))
