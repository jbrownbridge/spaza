from django.db import models

from shop.models.productmodel import Product as ShopProduct

class WholesalerChain(models.Model):
  name = models.CharField(max_length=256)

class Wholesaler(models.Model):
  name = models.CharField(max_length=256)
  chain = models.ForeignKey(WholesalerChain, blank=True, null=True)

  def __unicode__(self):
    if self.chain and len(str(self.chain)) > 0:
      return "%s: %s" % (self.chain, self.name)
    else:
      return self.name

class Manufacturer(models.Model):
  name = models.CharField(max_length=256)
 
  def __unicode__(self):
    return self.name

class WholesalerProduct(ShopProduct):
  wholesaler = models.ForeignKey(Wholesaler)
  manufacturer = models.ForeignKey(Manufacturer, blank=True, null=True)
  link = models.URLField(verify_exists=False)

