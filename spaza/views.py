from django.http import HttpResponse

def home(request):
	returnMessageFormat = "msisdn=%s&message=%s&serviceType=%s"
	msisdn      = request.REQUEST.get("msisdn", "no_cell_number")
	message     = request.REQUEST.get("message", "no_message")
	serviceType = "SESSION" 
	
	return HttpResponse(returnMessageFormat % (msisdn, message, serviceType))
	
