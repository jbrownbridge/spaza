from django.db import transaction

from commerce.api import get_cart_for_user

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

def save_address(*args, **kwargs):
  from spaza.models import Address
  from menus import USSDYesNoMenu, USSDAddressMenu
  current_address = kwargs.get('item', None)
  new_address = kwargs.get('string', None)
  session = kwargs.get('session', None)
  if session:
    if new_address:
      if not current_address:
        current_address = Address.objects.create(
          address=new_address,
          user_shipping=session.user,
          user_billing=session.user)
      else:
        current_address.address = new_address
        current_address.save()
      no_callback = USSDAddressMenu(back_menu=kwargs['parent'], address=current_address)
      title = "Your address is '%s'. Is this correct?" % current_address.address
      return USSDYesNoMenu(
        title, 
        back_menu=kwargs['parent'], 
        item=current_address, 
        yes_callback=checkout,
        no_callback=no_callback)
  return kwargs['parent']()

def get_address(*args, **kwargs):
  from spaza.models import Address
  from menus import USSDYesNoMenu, USSDAddressMenu
  session = kwargs.get('session', None)
  if session:
    user = session.user
    try:
      address = Address.objects.get(user_shipping=user)
    except Address.DoesNotExist:
      try:
        address = Address.objects.get(user_billing=user)
      except Address.DoesNotExist:
        address = None
    if address:
      no_callback = USSDAddressMenu(back_menu=kwargs['parent'], address=address)
      title = "Your address is '%s'. Is this correct?" % address.address
      return USSDYesNoMenu(
        title,
        back_menu=kwargs['parent'],
        item=address, 
        yes_callback=checkout,
        no_callback=no_callback)
  return USSDAddressMenu(back_menu=kwargs['parent']) 

def checkout(*args, **kwargs):
  from shop.models.ordermodel import Order
  from shop.models.cartmodel import CartItem
  session = kwargs.get('session', None)
  address = kwargs.get('item', None)
  if session and address:
    address = address.object
    cart = get_cart_for_user(session.user)
    cart.update()
    cart_size = CartItem.objects.filter(cart=cart).count()
    if cart_size > 0:
      try:
        with transaction.commit_on_success():
          order = Order.objects.create_from_cart(cart)
          order.set_shipping_address(address)
          order.set_billing_address(address)
          order.save()
          cart.empty()
        return USSDStartMenu() 
      except:
        if order:
          order.delete()
          transaction.commit()
  return kwargs['parent']()

def order_detail(*args, **kwargs):
  from menus import USSDOrderDetailMenu
  order = kwargs.get('item', None)
  if order:
    order = order.object
    title = "Order #%d: R%s (delivery included)" % (order.pk, order.order_total)
    return USSDOrderDetailMenu(title, back_menu=kwargs['parent'], order=order)
  return kwargs['parent']()

def order_item_detail(*args, **kwargs):
  from menus import USSDOrderItemDetailMenu
  item = kwargs.get('item', None)
  if item:
    item = item.object
    return USSDOrderItemDetailMenu(back_menu=kwargs['parent'], item=item)
  return kwargs['parent']()

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

