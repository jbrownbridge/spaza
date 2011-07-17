from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.utils.http import urlquote
from django.http import Http404

from spaza.ussd import *

import logging

log = logging.getLogger(__name__)

# Constants

USSD_FLASHMEDIA_NETWORKID_VODACOM = 1
USSD_FLASHMEDIA_NETWORKID_MTN = 2
USSD_FLASHMEDIA_NETWORKID_CELLC = 3

USSD_FLASHMEDIA_SERVICETYPE_FIRST = "FIRST"
USSD_FLASHMEDIA_SERVICETYPE_SESSION = "SESSION"
USSD_FLASHMEDIA_SERVICETYPE_END = "END"

USSD_FLASHMEDIA_SERVICETYPES = [
  USSD_FLASHMEDIA_SERVICETYPE_FIRST,
  USSD_FLASHMEDIA_SERVICETYPE_SESSION,
  USSD_FLASHMEDIA_SERVICETYPE_END,
]

USSD_FLASHMEDIA_MAXLENGTH_FIRST = 160
USSD_FLASHMEDIA_MAXLENGTH_SESSION = 182

USSD_FLASHMEDIA_MESSAGE_FORMAT = "msisdn=%s&message=%s&serviceType=%s"

def handle_restore(session):
  log.debug("Dead session brought back to life: %s" % session)
  session.current_menu = continue_from_last_time(session.current_menu)
  session.save()
  return str(session.current_menu)

def handle_session(session, message):
  session.current_menu = session.current_menu.answer(message)
  session.save()
  return str(session.current_menu)

def handle_start(session):
  session.current_menu = welcome()
  session.save()
  return str(session.current_menu)

def handle_end(request):
  session.current_menu = goodbye()
  session.save()
  auth.logout(request)
  return str(session.current_menu)

def flashmedia_response(msisdn, serviceType, message):
  return HttpResponse(USSD_FLASHMEDIA_MESSAGE_FORMAT % \
    (msisdn, urlquote(message), serviceType))

def flashmedia_end(msisdn, message = ""):
  return flashmedia_response(msisdn, USSD_FLASHMEDIA_SERVICETYPE_END, message)

def flashmedia_session(msisdn, message):
  return flashmedia_response( \
    msisdn, USSD_FLASHMEDIA_SERVICETYPE_SESSION, message)

def flashmedia_parse(session, msisdn, serviceType, message = ""):
  if serviceType == USSD_FLASHMEDIA_SERVICETYPE_END:
    return flashmedia_end(msisdn)
  else:
    # parse message
    if session.current_menu and not session.current_menu.is_finished():
      if   serviceType == USSD_FLASHMEDIA_SERVICETYPE_FIRST:
        response = handle_restore(session)
      elif serviceType == USSD_FLASHMEDIA_SERVICETYPE_SESSION:
        response = handle_session(session, message)
    else:
      response = handle_start(session)
    # handle response
    if session.current_menu.is_finished():
      return flashmedia_end(msisdn, response)
    else:
      return flashmedia_session(msisdn, response)
      
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

