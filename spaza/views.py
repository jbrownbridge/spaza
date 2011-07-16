from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth

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

@login_required
def handle_session(request, msisdn, message):
  try:
    menu = request.session['current_menu']
    menu = menu.answer(message)
    if menu:
      request.session['current_menu'] = menu
    else:
      del request.session['current_menu']
  except KeyError:
    log.warn("No current menu for %s's session for message: %s" % \
      (msisdn, message))
    menu = None
  return str(menu) if menu else ""

@login_required
def handle_start(request, msisdn):
  # Remove previous ussd menu state
  try:
    del request.session['current_menu']
  except KeyError:
    pass
  # Create new ussd menu state
  menu = welcome()
  request.session['current_menu'] = menu
  return str(menu) if menu else ""

@login_required
def handle_end(request, msisdn, message):
  try:
    del request.session['current_menu']
  except KeyError:
    pass
  auth.logout(request)
  return ""

@login_required
def flashmedia_ussd_landing_page(request):
  if request.method == 'GET':
    msisdn = request.GET.get('msisdn')
    message = request.GET.get('message')
    serviceType = request.GET.get('serviceType')
    if serviceType not in USSD_FLASHMEDIA_SERVICETYPES:
      log.error("Unknown serviceType for FlashMedia: %s (msisdn %s)" % \
        (serviceType, msisdn))
    else:
      if serviceType == USSD_FLASHMEDIA_SERVICETYPE_SESSION:
        response = handle_session(request, msisdn, message)
      elif serviceType == USSD_FLASHMEDIA_SERVICETYPE_FIRST:
        response = handle_start(request, msisdn)
      elif serviceType == USSD_FLASHMEDIA_SERVICETYPE_END:
        response = handle_end(request, msisdn, message)
      else:
        log.error("Unknown serviceType for FlashMedia: %s (msisdn %s)" % \
          (serviceType, msisdn))
        return HttpResponse(USSD_FLASHMEDIA_MESSAGE_FORMAT % \
          (msisdn, "", USSD_FLASHMEDIA_SERVICETYPE_END))

      menu = request.session.get('current_menu', None)
      
      # Check if there is a next menu if not then well end the session
      if menu:
        serviceType = USSD_FLASHMEDIA_SERVICETYPE_SESSION
      else:
        serviceType = USSD_FLASHMEDIA_SERVICETYPE_END

      return HttpResponse(USSD_FLASHMEDIA_MESSAGE_FORMAT % \
        (msisdn, response, serviceType))
  else:
    log.error("Post to flashmedia ussd landing page!")
  
  return HttpResponse(USSD_FLASHMEDIA_MESSAGE_FORMAT % \
    (msisdn, "", USSD_FLASHMEDIA_SERVICETYPE_END))

