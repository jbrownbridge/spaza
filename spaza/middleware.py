from django.conf import settings
from django.contrib import auth

import logging

log = logging.getLogger(__name__)

class SpazaMiddleware(object):
  """
  Middleware authenticates or creates a new user for each msisdn
  that enters the system.
  """

  def authenticate_user(self, request, msisdn):
    # First try to authenticate using msisdn
    if msisdn and len(msisdn) > 0:
      if request.user.username != msisdn:
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
        user = auth.authenticate(username=msisdn, password=msisdn)
        if user and user.is_active:
          auth.login(request, user)
          log.debug("Authenticated user for login: %s" % request.user)
          return user
    return None

  def process_request(self, request):
    # First try to authenticate using msisdn
    msisdn = request.GET.get('msisdn', None)
    if msisdn and len(msisdn) > 0:
      user = self.authenticate_user(request, msisdn)
    return None

