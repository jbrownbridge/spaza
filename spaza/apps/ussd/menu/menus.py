import logging

from items import *

log = logging.getLogger(__name__)

class USSDMenu(object):
  USSD_MAX_LENGTH = 190

  def __init__(self, title=None, back_menu=None, show_quit=True):
    self._title = title
    self._items = []
    self._show_quit = show_quit
    if back_menu:
      self._back_menu_callback = back_menu

  @property
  def title(self):
    return self._title

  @property
  def back_menu(self):
    if hasattr(self, '_back_menu_callback'):
      return self._back_menu_callback

  def is_finished(self):
    """
    This is overriden by USSDCloseMenu to indicate that we
    should return exit message
    """
    return False

  def add_item(self, description, callback):
    self._items.append(USSDMenuItem(description, callback))

  def add_database_item(self, description, callback, item):
    self._items.append(USSDDatabaseMenuItem(description, callback, item))

  @property
  def items(self):
    items = self._items[:]
    if self.back_menu:
      items.insert(0, USSDMenuItem("Back", self.back_menu))
    if self._show_quit:
      items.append(USSDMenuItem("Quit", USSDCloseMenu()))
    return items

  def get_item_text(self, item, short=False):
    if short and isinstance(item, USSDDatabaseMenuItem):
      return item.short_str
    else:
      return str(item)

  def get_menu_text(self, short=False):
    reply = "\n".join(
      map(
        lambda x, y: u"%d. %s" % (x, self.get_item_text(y, short)),
        range(1, len(self.items) + 1),
        self.items))
    if len(reply) > 0:
      reply = "\n".join([self.title, reply])
    else:
      reply = self.title
    return reply

  def __str__(self):
    reply = self.get_menu_text(short=False)
    if len(reply) > USSDMenu.USSD_MAX_LENGTH:
      reply = self.get_menu_text(short=True)
    return reply
 
  def answer(self, reply, *args, **kwargs):
    try:
      item = self.items[int(reply) - 1]
      callback = item.callback
      if hasattr(callback, '__call__'):
        return callback(parent=self, item=item, *args, **kwargs)
      else:
        return callback
    except:
      pass
    return self

class USSDListMenu(USSDMenu):
  """
  Menu that handles products by wrappin them in the item
  """
  
  def __init__(self, title, back_menu, objects, create_item_callback, item_callback, objects_per_page=5, page=1):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    super(USSDListMenu, self).__init__(title, back_menu)
    self._objects = objects
    self._create_item_callback = create_item_callback
    self._item_callback = item_callback
    self._objects_per_page = objects_per_page
    # Must make sure that products are assigned to local variable
    paginator = Paginator(self.objects, objects_per_page)
    try:
      self.__page = paginator.page(page)
    except PageNotAnInteger:
      self.__page = paginator.page(1)
    except EmptyPage:
      self.__page = paginator.page(paginator.num_pages)
  
  @property
  def title(self):
    parent_title = super(USSDListMenu, self).title
    if self.num_pages > 1:
      return "%s (%d/%d)" % ( \
        parent_title, 
        self.__page.number, 
        self.__page.paginator.num_pages)
    else:
      return parent_title

  @property
  def current_page_number(self):
    return self.__page.number

  @property
  def num_pages(self):
    return self.__page.paginator.num_pages

  @property
  def objects(self):
    if hasattr(self._objects, '__call__'):
      return self._objects()
    else:
      return self._objects

  def menu_for_page(self, page):
    return USSDListMenu(
      super(USSDListMenu, self).title, 
      self.back_menu, 
      self.objects,
      self._create_item_callback,
      self._item_callback,
      self._objects_per_page, 
      page)

  @property
  def previous_page(self):
    return USSDMenuItem(
      "^", self.menu_for_page(self.__page.previous_page_number()))
  
  @property
  def next_page(self):
    return USSDMenuItem(
      "v", self.menu_for_page(self.__page.next_page_number()))

  def add_item(self, description, callback):
    raise NotImplementedError
    
  @property
  def items(self):
    items = [USSDMenuItem("Back", self.back_menu)]
    for obj in self.__page.object_list:
      items.append(self._create_item_callback(obj, self._item_callback))
    #if self.__page.has_next(): 
    #if self.__page.has_previous():
    if self.num_pages > 1:
      items.insert(1, self.previous_page)
      items.append(self.next_page)
    return items

class USSDStringMenu(USSDMenu):
  def __init__(self, title, back_menu, item, callback):
    super(USSDStringMenu, self).__init__(title)
    self._callback = callback
    self._back_menu = back_menu
    self._item = item

  @property
  def items(self):
    return []

  def answer(self, reply, *args, **kwargs):
    try:
      return self._callback(parent=self._back_menu, string=reply, item=self._item, *args, **kwargs)
    except:
      pass
    return self._back_menu

class USSDQuantityMenu(USSDMenu):
  """
  Menu is overriden to take as reply a number instead of an item
  """
  def __init__(self, title, back_menu, item, callback):
    super(USSDQuantityMenu, self).__init__(title)
    self._callback = callback
    self._item = item
    self._back_menu = back_menu

  @property
  def items(self):
    return []

  def answer(self, reply, *args, **kwargs):
    try:
      try:
        quantity = int(reply)
      except:
        return self
      return self._callback(parent=self._back_menu, item=self._item, quantity=quantity, *args, **kwargs)
    except:
      pass
    return self._back_menu

class USSDHowManyMenu(USSDQuantityMenu):
  def __init__(self, item, back_menu, callback):
    text = "How many '%s' should I add to your trolley? Reply with the number or 0 for none."
    super(USSDHowManyMenu, self).__init__(text % str(item), back_menu, item, callback)

class USSDStartMenu(USSDMenu):
  """
  Menu is overriden to change the behaviour of session restore,
  since we don't really want to prompt to restore the first menu.
  """
  def __init__(self, user):
    from helpers import buy_stuff, help
    #from helpers import buy_stuff, where_is_my_stuff, what_are_people_buying, help
    super(USSDStartMenu, self).__init__("Welcome to Spaza.mobi")
    self.add_item("Buy Stuff", buy_stuff)
    self.add_item("Orders", USSDOrderMenu(self, user))
    #self.add_item("Where is my Stuff", where_is_my_stuff)
    #self.add_item("What are people buying", what_are_people_buying)
    self.add_item("Help", help)

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
    return self.title

class USSDContinueMenu(USSDMenu):
  """
  Continue method has slightly different behaviour than USSDMenu,
  instead of invoking a callback it stores menu items.
  """
  def __init__(self, old_menu, user):
    super(USSDContinueMenu, self).__init__("Continue from last time?")
    super(USSDContinueMenu, self).add_item("Yes", old_menu)
    super(USSDContinueMenu, self).add_item("No", USSDStartMenu(user))

  def add_item(self, description, callback):
    raise NotImplementedError

class USSDManufacturerListMenu(USSDListMenu):
  """
  Menu that handles products by wrappin them in the item
  """
  
  def __init__(self, back_menu, callback):
    from commerce.models import Manufacturer
    from items import create_manufacturer_menu_item
    manufacturers = Manufacturer.objects.all().exclude(name='').order_by('name')
    super(USSDManufacturerListMenu, self).__init__("Brands", back_menu, manufacturers, create_manufacturer_menu_item,callback)

class USSDManufacturerProductsListMenu(USSDListMenu):
  """
  Menu that handles products by wrappin them in the item
  """
  
  def __init__(self, manufacturer, back_menu, product_callback):
    from commerce.models import WholesalerProduct
    from items import create_product_menu_item
    title = "%s" % manufacturer.name
    products = WholesalerProduct.objects.filter(manufacturer=manufacturer).order_by('slug')
    super(USSDManufacturerProductsListMenu, self).__init__(title, back_menu, products, create_product_menu_item, product_callback)

class USSDProductListMenu(USSDListMenu):
  """
  Menu that handles products by wrappin them in the item
  """
  
  def __init__(self, title, back_menu, product_callback, products=None):
    from items import create_product_menu_item
    if not products:
      from commerce.models import Manufacturer, WholesalerProduct
      unknown = Manufacturer.objects.get(name="UNKNOWN")
      products = WholesalerProduct.objects.exclude(manufacturer=unknown).order_by('slug')
    super(USSDProductListMenu, self).__init__(title, back_menu, products, create_product_menu_item, product_callback)

class USSDProductDetailMenu(USSDMenu):
  def __init__(self, back_menu, product):
    from helpers import add_to_trolley
    super(USSDProductDetailMenu, self).__init__("%s @ R%s ea." % (product.name, product.unit_price), back_menu)
    callback = USSDHowManyMenu(product, back_menu, add_to_trolley)
    self.add_item("Add to trolley", callback)


class USSDModifyTrolleyMenu(USSDQuantityMenu):
  def __init__(self, item, back_menu, callback):
    text = "How many '%s' do you want in your trolley? Reply with the number or 0 for none."
    super(USSDModifyTrolleyMenu, self).__init__(text % str(item.product.name), back_menu, item, callback)

class USSDTrolleyItemDetailMenu(USSDMenu):
  def __init__(self, back_menu, item):
    from helpers import update_trolley, remove_from_trolley
    format = "Name: %s\nPrice: R%s\nNumber to buy: %d\nTotal: %d x R%s = R%s"
    product = item.product
    title = format % (\
      product.name, product.unit_price, item.quantity, 
      item.quantity, product.unit_price, item.line_total)
    super(USSDTrolleyItemDetailMenu, self).__init__(title, back_menu)
    update_callback = USSDModifyTrolleyMenu(item, back_menu, update_trolley)
    self.add_database_item("Change how many to buy", update_callback, item)
    self.add_database_item("Remove from trolley", remove_from_trolley, item)

class USSDTrolleyMenu(USSDListMenu):
  def __init__(self, back_menu, cart, cart_item_callback):
    from items import create_cart_menu_item
    from shop.models.cartmodel import CartItem
    cart.update()
    self._cart = cart
    super(USSDTrolleyMenu, self).__init__(
      "Trolley total is R%s" % cart.subtotal_price, 
      back_menu, 
      CartItem.objects.filter(cart=cart),
      create_cart_menu_item,
      cart_item_callback,
      objects_per_page=4)

  @property
  def items(self):
    from shop.models.cartmodel import CartItem
    items = super(USSDTrolleyMenu, self).items
    cart_size = CartItem.objects.filter(cart=self._cart).count()
    if cart_size > 0:
      items.append(USSDMenuItem("Go to till", USSDCheckoutMenu(self, self._cart)))
    return items

class USSDYesNoMenu(USSDMenu):
  def __init__(self, title, back_menu, item, yes_callback, no_callback=None):
    # No back menu
    super(USSDYesNoMenu, self).__init__(title, back_menu=back_menu, show_quit=False)
    if item:
      self.add_database_item("Yes", yes_callback, item)
    else:
      self.add_item("Yes", yes_callback)
    self.add_item("No", no_callback)

class USSDCheckoutMenu(USSDYesNoMenu):
  def __init__(self, back_menu, cart):
    from helpers import get_address
    cart.update()
    first_line = "Trolley items cost R%s and delivery costs R%s." % (cart.subtotal_price, cart.total_price - cart.subtotal_price)
    second_line = "You need to pay a total of R%s." % (cart.total_price)
    third_line = "Choose Yes to take your trolley to the till or No to go back."
    title = "%s %s %s" % (first_line, second_line, third_line)
    super(USSDCheckoutMenu, self).__init__(title, None, None, get_address, back_menu)

class USSDAddressMenu(USSDStringMenu):
  """
  We need an address to send it to
  """
  def __init__(self, back_menu, address=None):
    from helpers import save_address
    title = "Where must we send your goods (please reply with an address that a taxi could find)?"
    super(USSDAddressMenu, self).__init__(title, back_menu, address, save_address)

class USSDOrderMenu(USSDMenu):
  def __init__(self, back_menu, user):
    from shop.models.ordermodel import Order
    from helpers import order_detail
    super(USSDOrderMenu, self).__init__("Orders", back_menu)
    payment_required = Order.objects.filter(user=user).filter(status__lt=Order.COMPLETED).order_by('-modified')
    payment_received = Order.objects.filter(user=user).filter(status__gte=Order.COMPLETED).order_by('-modified')
    self.add_item("I must still pay for", 
      USSDOrderListMenu("I must still pay for", self, order_detail, payment_required))
    self.add_item("I have payed for",
      USSDOrderListMenu("I have payed for", self, order_detail, payment_received))

class USSDOrderListMenu(USSDListMenu):
  """
  Menu that handles products by wrappin them in the item
  """
  def __init__(self, title, back_menu, order_callback, orders):
    from items import create_order_menu_item
    super(USSDOrderListMenu, self).__init__(title, back_menu, orders, create_order_menu_item, order_callback)

class USSDOrderDetailMenu(USSDListMenu):
  def __init__(self, title, back_menu, order):
    from items import create_order_item_menu_item
    from shop.models.ordermodel import OrderItem
    from helpers import order_item_detail
    super(USSDOrderDetailMenu, self).__init__(
      title, 
      back_menu, 
      OrderItem.objects.filter(order=order),
      create_order_item_menu_item,
      order_item_detail,
      objects_per_page=4)

class USSDOrderItemDetailMenu(USSDMenu):
  def __init__(self, back_menu, item):
    title = "%dx%s=R%s" % (item.quantity, item.product_name, item.line_total)
    super(USSDOrderItemDetailMenu, self).__init__(title, back_menu, show_quit=False)

