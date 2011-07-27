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

def create_product_menu_item(x, callback):
  return USSDDatabaseMenuItem("%s R%s" % (x.name.split(':')[1], x.unit_price), callback, x)

def create_cart_menu_item(cart_item, callback):
  cart_item.update()
  product_string = str(cart_item.product)
  if len(product_string) > 20:
    product_string = product_string[:20]
    product_string += "..."
  line_item = "%dx%s=R%s" % ( \
    cart_item.quantity, 
    product_string, 
    cart_item.line_total)
  return USSDDatabaseMenuItem(line_item, callback, cart_item)

