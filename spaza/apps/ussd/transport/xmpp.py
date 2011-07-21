#from django.core.management import setup_environ
#from spaza import settings

#setup_environ(settings)

from twisted.words.xish import domish
from twisted.words.protocols.jabber.jid import JID
from wokkel import client, xmppim
from ussd.menu import *

import logging

log = logging.getLogger(__name__)

from ussd.api import handle_restore, handle_session, handle_start, handle_end
from ussd.backend import USSDAuthBackend
from ussd.models import USSDSession

class JabberProtocol(
  xmppim.MessageProtocol, 
  xmppim.PresenceClientProtocol, 
  xmppim.RosterClientProtocol):
  
  def __init__(self, message_handler=None):
    xmppim.MessageProtocol.__init__(self)
    self.message_handler = message_handler

  def connectionInitialized(self):
    xmppim.MessageProtocol.connectionInitialized(self)
    xmppim.PresenceClientProtocol.connectionInitialized(self)
    xmppim.RosterClientProtocol.connectionInitialized(self)
    self.xmlstream.send(xmppim.AvailablePresence())
    self.roster = self.getRoster()

  def connectionMade(self):
    print "Connection Made"

  def subscribeReceived(self, entity):
    xmppim.PresenceClientProtocol.subscribe(self, entity)
    log.info(u"Received and accepted subscription request from %s",
       entity.full())

  def unsubscribeReceived(self, entity):
    xmppim.PresenceClientProtocol.unsubscribe(self, entity)
    log.info(u"Received and accepted unsubscribe request from %s",
       entity.full())

  def onMessage(self, msg):
    log.debug(u"Received %s message from %s: %s", 
      msg['type'], msg['from'], msg.body)

    if msg['type'] == 'chat' and hasattr(msg, 'body') and msg.body:
      if self.message_handler:
        self.message_handler.answer(
          transport = self.chat,
          recipient = msg['from'],
          message = msg.body)
      else:
        print "Message from %s: %s" % (msg['from'], msg.body)
        self.chat(msg['from'], "Message received sir!")

  def chat(self, to, body):
    reply = domish.Element((None, 'message'))
    reply['to'] = to
    reply['from'] = self.parent.jid.full()
    reply['type'] = 'chat'
    reply.addElement('body', content=body)
    xmppim.MessageProtocol.send(self, reply)
    log.debug(u"Sent %s reply to %s: %s", 
      reply['type'], reply['to'], reply.body)

class XMPPMessageHandler(object):
  def __init__(self):
    self._current_menu = None
    self.auth = USSDAuthBackend()

  def answer(self, transport, recipient, message):
    user = self.auth.authenticate(recipient)
    if user:
      session = USSDSession.objects.recent(user)
      if session:
        log.debug("User: %s USSD Session: %s" % (user, session))
        msg = str(message)
        if msg == "$start":
          response = handle_start(session)
        elif msg == "$end":
          response = handle_end(session)
        else:
          if session.current_menu and not session.current_menu.is_finished():
            response = handle_session(session, msg)
          else:
            response = "Use $start to create menu"
        transport(recipient, response)
        return
      else:
        transport(recipient, "Error: No USSD Session!")
    else:
      transport(recipient, "Error: No User!")


class XMPPClient(client.XMPPClient):
  def __init__(self, username, password, host, port, message_handler=None):
    super(XMPPClient, self).__init__(JID(username), password, host, port)
    self.logTraffic = False
    message_handler = XMPPMessageHandler()
    jabber_handler = JabberProtocol(message_handler)
    jabber_handler.setHandlerParent(self)
