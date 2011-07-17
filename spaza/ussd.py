# FIXME:    This is django ugliness, we should either choose to make the whole
#           thing a Django app or we should remove the dependency entirely
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'spaza.settings'

from django.conf import settings
from spaza.models import Product

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
 
  def answer(self, reply):
    try:
      return self.items[int(reply) - 1].callback()
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

  def answer(self, reply):
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

def buy_stuff():
  menu = USSDMenu("Buy Stuff")
  for product in Product.objects.all():
    menu.add_item("%s - R%s" % (product.name, product.price), buy_stuff)
  return menu

def where_is_my_stuff():
  menu = USSDMenu("Where is my Stuff")
  return menu

def what_are_people_buying():
  menu = USSDMenu("What are people buying")
  return menu

def help():
  menu = USSDMenu("No help - so ure screwed!")
  return menu

def welcome():
  return USSDStartMenu()

def goodbye():
  return USSDCloseMenu()

def continue_from_last_time(old_menu):
  if isinstance(old_menu, USSDContinueMenu):
    return old_menu
  elif isinstance(old_menu, USSDStartMenu):
    return old_menu
  else:
    return USSDContinueMenu(old_menu)

