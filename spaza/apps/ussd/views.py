from django.contrib.auth.decorators import login_required
from django.http import Http404

from ussd.transport.flashmedia import *

import logging

log = logging.getLogger(__name__)

@login_required
def flashmedia_landing_page(request):
  user = request.user
  msisdn = request.GET.get('msisdn', None)
  ussd_session = request.session.get('ussd_session', None)
  serviceType = request.GET.get('serviceType', None)
  msg = request.GET.get('message', None)
  if not user:
    log.error("No user even though login_required")
    raise Http404
  elif not msisdn:
    log.error("No msisdn associated with user: %s" % user)
    raise Http404
  elif not ussd_session:
    log.error("No ussd session associated with user: %s" % user)
    raise Http404
  elif not serviceType:
    log.error("No service type associated with user: %s" % user)
    raise Http404
  elif serviceType not in USSD_FLASHMEDIA_SERVICETYPES:
    log.error("Unknown serviceType %s for FlashMedia with user: %s" % \
      (serviceType, user))
    raise Http404
  else:
    if request.method == 'GET':
      log.debug("User: %s Django Session: %s, USSD Session: %s" % ( \
        user, 
        request.session.session_key,
        request.session.get('ussd_session', None)))
      return flashmedia_parse(ussd_session, msisdn, serviceType, msg)
    else:
      log.error("Unexpected POST to FlashMedia landing page!")
      raise Http404

