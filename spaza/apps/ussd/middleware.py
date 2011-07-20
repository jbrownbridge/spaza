from django.conf import settings
from django.contrib import auth

from ussd.models import USSDSession

import logging

log = logging.getLogger(__name__)

class USSDMiddleware(object):
  """
  Middleware authenticates or creates a new user for each valid id
  that enters the system.
  """

  def authenticate_user(self, request, username):
    # First try to authenticate using username
    if username and len(username) > 0:
      if request.user.username != username:
        auth.logout(request)
        authenticated = False
      else:
        authenticated = request.user.is_authenticated()
      if authenticated:
        if request.user.is_active:
          return request.user
        else:
          auth.logout(request)
          log.debug("Authenticated inactive user forcibly logged-out: %s" % \
            request.user)
      else:
        user = auth.authenticate(username=username, password=username)
        if user and user.is_active:
          auth.login(request, user)
          log.debug("Authenticated user for login: %s" % request.user)
          return user
    return None

  def process_request(self, request):
    msisdn = request.GET.get('msisdn', None)
    # First try to authenticate using msisdn
    if msisdn and len(msisdn) > 0:
      username = msisdn
    else:
      return None
    user = self.authenticate_user(request, username)
    request.session['ussd_session'] = USSDSession.objects.recent(user)
    return None

