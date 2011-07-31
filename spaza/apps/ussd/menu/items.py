import logging

log = logging.getLogger(__name__)

class USSDMenuItem(object):
  def __init__(self, description, callback):
    self.description = str(description).strip()
    self.callback = callback

  def __str__(self):
    return self.description

class USSDDatabaseMenuItem(USSDMenuItem):
  def __init__(self, description, callback, object):
    super(USSDDatabaseMenuItem, self).__init__(description, callback)
    self._object = object

  @property
  def short_str(self):
    if len(self.description) <= 20:
      return str(self.description)
    else:
      shortened = str(self.description[:17])
      shortened += "..."
      return shortened

  @property
  def object(self):
    return self._object

def shorten(text, max_length=20):
  if len(text) <= max_length:
    return str(text)
  else:
    return str(text)[:17] + "..."

def create_manufacturer_menu_item(x, callback):
  return USSDDatabaseMenuItem(shorten(x.name), callback, x)

def create_product_menu_item(x, callback):
  product_string = "%s R%s" % (shorten(x.name.split(':')[1]), x.unit_price)
  return USSDDatabaseMenuItem(product_string, callback, x)

def create_order_menu_item(x, callback):
  order_string = "Order #%d: R%s" % (x.pk, x.order_total)
  return USSDDatabaseMenuItem(order_string, callback, x)

def create_order_item_menu_item(order_item, callback):
  line_item = "%dx%s=R%s" % ( \
    order_item.quantity,
    shorten(str(order_item.product_name)),
    order_item.line_total)
  return USSDDatabaseMenuItem(line_item, callback, order_item)

def create_cart_menu_item(cart_item, callback):
  cart_item.update()
  line_item = "%dx%s=R%s" % ( \
    cart_item.quantity,
    shorten(str(cart_item.product)),
    cart_item.line_total)
  return USSDDatabaseMenuItem(line_item, callback, cart_item)

