from django.db import models
from django.conf import settings

class Vendor(models.Model):
    name = models.CharField(max_length=256)
    telnum = models.CharField(max_length=256)
    info = models.TextField()

class Supplier(models.Model):
    pass
#more to be added here

class Product(models.Model):
  code = models.CharField(max_length=256)
  name = models.CharField(max_length=256)
  description = models.TextField()
  price = models.DecimalField(max_digits=19, decimal_places=2)

  def __unicode__(self):
    return u"%s: %s" % (self.code, self.name)

class Category(models.Model):
    pass
#more to be added here

class Cart(models.Model):
    pass
#more to come

class Order(models.Model):
    pass
#more to come

class CartItem(models.Model):
    pass
#more to come

class OrderItem(models.Model):
    pass
#more to come
