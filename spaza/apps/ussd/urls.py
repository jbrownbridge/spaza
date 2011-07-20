from django.conf.urls.defaults import url, patterns
from ussd.views import flashmedia_landing_page

urlpatterns = patterns('ussd.views',
  (r'^$',             flashmedia_landing_page),
  # Hack for FlashMedia because MTN not updating
  (r'^test\.php/?$',  flashmedia_landing_page),
)
