from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

SIMPLE_ADDRESS_TEMPLATE = \
_("""
Name: %(name)s,
Address: %(address)s,
""")

class Address(models.Model):
  user_shipping = models.OneToOneField(User, related_name='shipping_address',
                                      blank=True, null=True)
  user_billing = models.OneToOneField(User, related_name='billing_address',
                                      blank=True, null=True)

  name = models.CharField(_('Name'), max_length=255)
  address = models.CharField(_('Address'), max_length=255)

  class Meta(object):
    verbose_name = _('Address')
    verbose_name_plural = _("Addresses")

  def __unicode__(self):
    return '%s (%s)' % (self.name, self.address)

  def clone(self):
    new_kwargs = dict([(fld.name, getattr(self, fld.name))
                        for fld in self._meta.fields if fld.name != 'id'])
    return self.__class__.objects.create(**new_kwargs)

  def as_text(self):
    return SIMPLE_ADDRESS_TEMPLATE % {
      'name':self.name, 'address':self.address
    }


