from django.conf.urls.defaults import *

from shop import urls as shop_urls
from ussd import urls as ussd_urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # default here if nothing matches
    (r'^$',       include(ussd_urls)),
    (r'^admin/',  include(admin.site.urls)),
    (r'^ussd/',   include(ussd_urls)),
    (r'^shop/',   include(shop_urls)), # <-- That's the important bit
    # Example:
    # (r'^spaza/', include('spaza.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
)
