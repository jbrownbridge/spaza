from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from shop_simplecategories.models import Category
from commerce.models import Wholesaler, Manufacturer
from commerce.models import WholesalerProduct as Product
from decimal import *

import json

class Command(BaseCommand):
  args = '<input_file>'
  help = 'This command takes generated test data and imports into database'
  
  def __init__(self, *args, **kwargs):
    super(Command, self).__init__(*args, **kwargs)
    self.cache = {}
    self.names = {}

  def handleCategories(self, category_list=[]):
    """
    Gets a list of strings, and returns a database category item
    for product.
    """
    if len(category_list) == 0:
      return None
    prev = None
    for curr in category_list:
      curr = self.__c(curr)
      if curr in self.cache:
        # Database object exists in cache so use it
        prev = self.cache[curr]
      else:
        # No database object in cache so get or create it
        prev = Category.objects.get_or_create(name=curr, parent_category=prev)[0]
        # Store object in cache
        self.cache[curr] = prev
    return prev

  def __c(self, s):
    from django.utils.html import escape
    return s.encode('ascii', 'xmlcharrefreplace').strip()

  def getManufacturer(self, name):
    unknown = Manufacturer.objects.get_or_create(name='UNKNOWN')[0]
    name_array = name.split(':')
    if len(name_array) == 1:
      return unknown
    else:
      return Manufacturer.objects.get_or_create(name=name_array[0].strip().upper())[0]

  def importMakroProducts(self, wholesaler, products):
#     data.append({
#       'brand' : brand,
#       'variation' : variation,
#       'sku' : sku,
#       'product_id' : product_id,
#       'link' : link,
#       'price' : price,
#     })
    for product in products:
      category = self.handleCategories(product['categories'])
      name = "%s: %s" % (product['brand'], product['variation'])
      name = self.__c(name)
      if not name in self.names:
        self.names[name] = True
        p, created = Product.objects.get_or_create(
          name = name,
          unit_price = Decimal(product['price']) \
            .quantize(Decimal('.01'), rounding=ROUND_DOWN),
          wholesaler = wholesaler,
          link = product['link'],
          manufacturer = self.getManufacturer(name),
        )
        if created:
          p.slug = slugify(p.name)
          if category: p.categories.add(category) 
          p.save()

  def importWoolworthsProducts(self, wholesaler, products):
#     data.append({
#       'name' : name,
#       'link' : link,
#       'product_id' : product_id,
#       'price' : price,
#     })
    for product in products:
      category = self.handleCategories(product['categories'])
      name = "%s" % (product['name'])
      name = self.__c(name)
      if not name in self.names:
        self.names[name] = True
        p, created = Product.objects.get_or_create(
          name = name,
          unit_price = Decimal(product['price']) \
            .quantize(Decimal('.01'), rounding=ROUND_DOWN),
          wholesaler = wholesaler,
          link = product['link'],
          manufacturer = self.getManufacturer(name),
        )
        if created:
          p.slug = slugify(p.name)
          if category: p.categories.add(category)
          p.save()

  def handle(self, *args, **options):
    if len(args) == 1:
      filename = args[0]
      with open(filename, mode='r') as f:
        data = json.load(f)
      woolworthsProducts = data['Woolworths']
      makroProducts = data['Makro']
      woolworths = Wholesaler.objects.get_or_create(name='Woolworths')[0]
      makro = Wholesaler.objects.get_or_create(name='Makro')[0]
      self.importMakroProducts(makro, makroProducts)
      self.importWoolworthsProducts(woolworths, woolworthsProducts)
    else:
      print "You need to specify the input filename"

      
