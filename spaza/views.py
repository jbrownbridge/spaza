from django.http import HttpResponse

import logging

log = logging.getLogger(__name__)

def home(request):
	returnMessageFormat = "msisdn=%s&message=%s&serviceType=%s"
	msisdn        = request.REQUEST.get("msisdn", "no_cell_number")
	message       = request.REQUEST.get("message", "no_message")
	serviceType   = "SESSION" 
	returnMessage = returnMessageFormat % (msisdn, message, serviceType)
	log.debug("Responded with: %s" % (returnMessage))	
	return HttpResponse(returnMessage)
	
