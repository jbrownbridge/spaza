# FIXME:    This is django ugliness, we should either choose to make the whole
#           thing a Django app or we should remove the dependency entirely
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'spaza.settings'

from django.conf import settings
from spaza.models import Product

class USSDMenu(object):
  def __init__(self, title=None):
    self._title = title
    self._items = []

  def add_item(self, description, callback):
    self._items.append(USSDMenuItem(description, callback))

  def __str__(self):
    reply = "\\n".join(
      map(
        lambda x, y: u"%d. %s" % (x, str(y)),
        range(1, len(self._items) + 1),
        self._items))
    if self._title:
      if len(reply) > 0:
        reply = "\\n".join([self._title, reply])
      else:
        reply = self._title
    return reply
 
  def answer(self, reply):
    try:
      return self._items[int(reply) - 1].callback()
    except:
      pass
    return self

class USSDMenuItem(object):
  def __init__(self, description, callback):
    self.description = description
    self.callback = callback

  def __str__(self):
    return self.description

#Buy Stuff Menus and Submenus
def buy_stuff():
  menu = USSDMenu("Buy Stuff")
  menu.add_item("List Products", list_products) #later to become search/browse by category
  menu.add_item("List Items in cart", list_items_in_cart)
  menu.add_item("Checkout", checkout)
  return menu

def list_products():
  menu - USSDMenu("Products")
  for product in Product.objects.all():
    menu.add_item("%s - R%s" % (product.name, product.price), product_menu)
  return menu

def list_items_in_cart():
    pass

def checkout():
    pass

def product_menu():
    menu = USSDMenu("Product")
    menu.add_item("Add to Cart", add_to_cart)
    menu.add_item("View Description", view_description)
    menu.add_item("Back", buy_stuff)
    return menu

def add_to_cart():
    #check if cart already exists
    #if not: create new and add to cart
    #else: add to existing cart
    pass

def view_description():
    pass

#Where is my stuff menus and submenus
def where_is_my_stuff():
  menu = USSDMenu("Where is my Stuff")
  return menu

#What are people buying menus and submenus
def what_are_people_buying():
  menu = USSDMenu("What are people buying")
  return menu

#Help menu
def help():
  menu = USSDMenu("No help - so ure screwed!")
  return menu

def welcome():
  menu = USSDMenu("Welcome to Spaza.mobi")
  menu.add_item("Buy Stuff", buy_stuff)
  menu.add_item("Where is my Stuff", where_is_my_stuff)
  menu.add_item("What are people buying", what_are_people_buying)
  menu.add_item("Help", help)
  return menu


  
  
