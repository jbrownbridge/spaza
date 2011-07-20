from django.http import HttpResponse
from django.utils.http import urlquote

from ussd.api import *

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

