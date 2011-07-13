from django.conf.urls.defaults import *
from spaza.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^emulator/?', emulator),
  (r'^admin/', include(admin.site.urls)),
  (r'^.*/?$', home),
    # Example:
    # (r'^spaza/', include('spaza.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
)
