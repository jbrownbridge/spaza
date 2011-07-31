""" Cart modifierts for the myshop app of django-shop-adventures."""
import decimal

from django.conf import settings

from shop.cart.cart_modifiers_base import BaseCartModifier

class FixedShippingCosts(BaseCartModifier):
  """
  This will add a fixed amount of money for shipping costs.
  """
  def add_extra_cart_price_field(self, cart):
    rate = decimal.Decimal(settings.SHOP_SHIPPING_FLAT_RATE)
    cart.extra_price_fields.append(('Delivery costs', rate))
    return cart
