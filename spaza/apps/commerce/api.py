from shop.models.cartmodel import Cart

import logging

log = logging.getLogger(__name__)

def get_cart_for_user(user):
  cart, created = Cart.objects.get_or_create(user=user)
  if created:
    log.info("Created new cart for user: %s" % user)
  else:
    cart.update()
    log.debug("Loaded existing cart for user: %s" % user)
  return cart
