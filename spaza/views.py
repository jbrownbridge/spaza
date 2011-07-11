from django.http import HttpResponse

def home(request):
	if request.method == 'GET':
		return HttpResponse("GET request")
	elif request.method == 'POST':
		return HttpResponse("POST request")
	else:
		pass
	
