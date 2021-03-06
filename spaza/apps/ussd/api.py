import logging

from ussd.menu.helpers import *

log = logging.getLogger(__name__)

def handle_restore(session):
  log.debug("Dead session brought back to life: %s" % session)
  session.current_menu = continue_from_last_time(session.current_menu, session=session)
  session.save()
  return str(session.current_menu)

def handle_session(session, message):
  session.current_menu = session.current_menu.answer(message, session=session)
  session.save()
  return str(session.current_menu)

def handle_start(session):
  session.current_menu = welcome(session=session)
  session.save()
  return str(session.current_menu)

def handle_end(session):
  session.current_menu = goodbye(session=session)
  session.save()
  return str(session.current_menu)

