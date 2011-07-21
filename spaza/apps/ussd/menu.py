from django.conf import settings
from commerce.models import WholesalerProduct as Product
from commerce.api import get_cart_for_user
from shop.models.cartmodel import CartItem

import logging

log = logging.getLogger(__name__)

class USSDMenuItem(object):
  def __init__(self, description, callback):
    self.description = description
    self.callback = callback

  def __str__(self):
    return self.description

class USSDMenu(object):
  def __init__(self, title=None):
    self._title = title
    self._items = []
    self._quit_item = USSDMenuItem("Quit", goodbye)

  def is_finished(self):
    """
    This is overriden by USSDCloseMenu to indicate that we
    should return exit message
    """
    return False

  def add_item(self, description, callback):
    self._items.append(USSDMenuItem(description, callback))

  @property
  def items(self):
    items = self._items[:]
    items.append(self._quit_item)
    return items

  def __str__(self):
    reply = "\n".join(
      map(
        lambda x, y: u"%d. %s" % (x, str(y)),
        range(1, len(self.items) + 1),
        self.items))
    if self._title:
      if len(reply) > 0:
        reply = "\n".join([self._title, reply])
      else:
        reply = self._title
    return reply
 
  def answer(self, reply, *args, **kwargs):
    try:
      return self.items[int(reply) - 1].callback(*args, **kwargs)
    except:
      pass
    return self

class USSDCloseMenu(USSDMenu):
  """
  Used to signify the end of menus
  """
  def __init__(self):
    super(USSDCloseMenu, self).__init__("Goodbye!")
  
  def is_finished(self):
    """
    Overriden to exit menu
    """
    return True

  def add_item(self, description, callback):
    raise NotImplementedError

  def __str__(self):
    return self._title

class USSDContinueMenu(USSDMenu):
  """
  Continue method has slightly different behaviour than USSDMenu,
  instead of invoking a callback it stores menu items.
  """
  def __init__(self, old_menu):
    super(USSDContinueMenu, self).__init__("Continue from last time?")
    super(USSDContinueMenu, self).add_item("Yes", old_menu)
    super(USSDContinueMenu, self).add_item("No", welcome())

  def add_item(self, description, callback):
    raise NotImplementedError

  def answer(self, reply, *args, **kwargs):
    try:
      return self.items[int(reply) -1].callback
    except:
      pass
    return self

class USSDStartMenu(USSDMenu):
  """
  Menu is overriden to change the behaviour of session restore,
  since we don't really want to prompt to restore the first menu.
  """
  def __init__(self):
    super(USSDStartMenu, self).__init__("Welcome to Spaza.mobi")
    self.add_item("Buy Stuff", buy_stuff)
    self.add_item("Where is my Stuff", where_is_my_stuff)
    self.add_item("What are people buying", what_are_people_buying)
    self.add_item("Help", help)

#Buy Stuff Menus and Submenus
def buy_stuff(*args, **kwargs):
  menu = USSDMenu("Buy Stuff")
  menu.add_item("List Products", list_products) #later to become search/browse by category
  menu.add_item("List Items in cart", list_items_in_cart)
  menu.add_item("Checkout", checkout)
  return menu

def list_products(*args, **kwargs):
  menu = USSDMenu("Products")
  for product in Product.objects.all():
    menu.add_item("%s - R%s" % (product.name, product.unit_price), product_menu)
  return menu

def list_items_in_cart(*args, **kwargs):
    menu = USSDMenu("Cart Items")
    session = kwargs.get('session', None)
    if session:
      cart = get_cart_for_user(session.user)
      for item in CartItem.objects.filter(cart=cart):
        item.update()
        menu.add_item(str(item), None)
    return menu

def checkout(*args, **kwargs):
    pass

def product_menu(*args, **kwargs):
    menu = USSDMenu("Product")
    menu.add_item("Add to Cart", add_to_cart)
    menu.add_item("View Description", view_description)
    menu.add_item("Back", buy_stuff)
    return menu

def add_to_cart(*args, **kwargs):
    return product_menu()
    #check if cart already exists
    #if not: create new and add to cart
    #else: add to existing cart
    pass

def view_description(*args, **kwargs):
    pass

#Where is my stuff menus and submenus
def where_is_my_stuff(*args, **kwargs):
  menu = USSDMenu("Where is my Stuff")
  return menu

#What are people buying menus and submenus
def what_are_people_buying(*args, **kwargs):
  menu = USSDMenu("What are people buying")
  return menu

#Help menu
def help(*args, **kwargs):
  menu = USSDMenu("No help - so ure screwed!")
  return menu

def welcome(*args, **kwargs):
  return USSDStartMenu()

def goodbye(*args, **kwargs):
  return USSDCloseMenu()

def continue_from_last_time(old_menu, *args, **kwargs):
  if isinstance(old_menu, USSDContinueMenu):
    return old_menu
  elif isinstance(old_menu, USSDStartMenu):
    return old_menu
  else:
    return USSDContinueMenu(old_menu)

