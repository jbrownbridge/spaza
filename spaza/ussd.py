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

def buy_stuff():
  menu = USSDMenu("Buy Stuff")
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
  menu = USSDMenu("Welcome to Spaza.mobi")
  menu.add_item("Buy Stuff", buy_stuff)
  menu.add_item("Where is my Stuff", where_is_my_stuff)
  menu.add_item("What are people buying", what_are_people_buying)
  menu.add_item("Help", help)
  return menu


  
  
