from django.conf import settings
from commerce.api import get_cart_for_user
from shop.models.cartmodel import CartItem

from menus import USSDMenu, USSDStartMenu, USSDCloseMenu, USSDContinueMenu
from menus import USSDManufacturerListMenu
from menus import USSDManufacturerProductsListMenu, USSDProductListMenu, USSDProductDetailMenu
from menus import USSDTrolleyMenu, USSDTrolleyItemDetailMenu

from items import *

log = logging.getLogger(__name__)

#Buy Stuff Menus and Submenus
def buy_stuff(*args, **kwargs):
  menu = USSDMenu("Buy Stuff", back_menu=kwargs['parent'])
  menu.add_item("Show products", list_manufacturers) #later to become search/browse by category
  menu.add_item("Show trolley", list_items_in_trolley)
  menu.add_item("Empty trolley", empty_trolley)
  #menu.add_item("Pay for trolley", checkout)
  return menu

def empty_trolley(*args, **kwargs):
  menu = USSDMenu("Cart Items", back_menu=kwargs['parent'])
  session = kwargs.get('session', None)
  if session:
    cart = get_cart_for_user(session.user)
    if cart:
      cart.empty()
  return kwargs['parent']() 

def list_manufacturers(*args, **kwargs):
  return USSDManufacturerListMenu(kwargs['parent'], list_products_per_manufacturer)

def list_products_per_manufacturer(*args, **kwargs):
  manufacturer = kwargs.get('item').object
  return USSDManufacturerProductsListMenu(
    manufacturer, kwargs['parent'], product_detail)

def list_products(*args, **kwargs):
  return USSDProductListMenu("Products", kwargs['parent'], product_detail)

def list_items_in_trolley(*args, **kwargs):
  session = kwargs.get('session', None)
  if session:
    cart = get_cart_for_user(session.user)
    return USSDTrolleyMenu(
      back_menu=kwargs['parent'],
      cart=cart,
      cart_item_callback=trolley_item_detail)
  return kwargs['parent']()

def checkout(*args, **kwargs):
    pass

def product_detail(*args, **kwargs):
  return USSDProductDetailMenu(back_menu=kwargs['parent'], product=kwargs['item'].object)

def trolley_item_detail(*args, **kwargs):
  return USSDTrolleyItemDetailMenu(back_menu=kwargs['parent'], item=kwargs['item'].object)

def update_trolley(*args, **kwargs):
  session = kwargs.get('session', None)
  if session:
    item = kwargs.get('item', None)
    quantity = kwargs.get('quantity', 0)
    if item and quantity > 0:
      cart = get_cart_for_user(session.user)
      cart.update_quantity(item.pk, quantity)
      cart.update()
      cart.save()
  return USSDTrolleyMenu(kwargs['parent'], cart, trolley_item_detail)

def remove_from_trolley(*args, **kwargs):
  session = kwargs.get('session', None)
  if session:
    item = kwargs.get('item', None).object
    if item:
      cart = get_cart_for_user(session.user)
      cart.delete_item(item.pk)
      cart.update()
      cart.save()
  pdb.set_trace()
  return USSDTrolleyMenu(kwargs['parent'], cart, trolley_item_detail)

def add_to_trolley(*args, **kwargs):
  session = kwargs.get('session', None)
  if session:
    product = kwargs.get('item', None)
    quantity = kwargs.get('quantity', 0)
    if product and quantity > 0:
      cart = get_cart_for_user(session.user)
      cart.add_product(product, quantity)
      cart.update()
      cart.save()
  return USSDTrolleyMenu(kwargs['parent'], cart, trolley_item_detail)

#Where is my stuff menus and submenus
def where_is_my_stuff(*args, **kwargs):
  menu = USSDMenu("Where is my Stuff", back_menu=kwargs['parent'])
  return menu

#What are people buying menus and submenus
def what_are_people_buying(*args, **kwargs):
  menu = USSDMenu("What are people buying", back_menu=kwargs['parent'])
  return menu

#Help menu
def help(*args, **kwargs):
  menu = USSDMenu("No help - so ure screwed!", back_menu=kwargs['parent'])
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

