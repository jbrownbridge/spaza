from django.contrib import admin
from shop_simplecategories.admin import ProductWithCategoryForm
from commerce.models import *

class ProductForm(ProductWithCategoryForm):
  class Meta(object):
    model = WholesalerProduct

class WholesalerProductAdmin(admin.ModelAdmin):
  form = ProductForm
  prepopulated_fields = {"slug" : ("name", )}

admin.site.register(WholesalerChain)
admin.site.register(Wholesaler)
admin.site.register(WholesalerProduct, WholesalerProductAdmin)

