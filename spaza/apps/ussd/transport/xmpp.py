from twisted.words.xish import domish
from twisted.words.protocols.jabber.jid import JID
from wokkel import client, xmppim
from ussd.menu import *

from twisted.python import log

import logging

# Evil I know :(
log.debug = lambda x: log.msg(x, logLevel=logging.DEBUG)
log.info = lambda x: log.msg(x, logLevel=logging.WARN)
log.error = lambda x: log.msg(x, logLevel=logging.ERROR)

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
    log.debug("Connection Made")

  def subscribeReceived(self, entity):
    xmppim.PresenceClientProtocol.subscribe(self, entity)
    log.info(u"Received and accepted subscription request from %s" % entity.full())

  def unsubscribeReceived(self, entity):
    xmppim.PresenceClientProtocol.unsubscribe(self, entity)
    log.info(u"Received and accepted unsubscribe request from %s" % entity.full())

  def onMessage(self, msg):
    log.debug(u"Received %s message from %s: %s" % (msg['type'], msg['from'], msg.body))

    if msg.x and msg.x.defaultUri == 'jabber:x:delay':
      log.debug(u"Ignoring delayed message")
      return

    if msg.body is None:
      log.debug(u'Ignoring empty message')
      self.chat(msg['from'], "Use $start to create menu")
      return

    try:
      if msg['type'] == 'error':
        log.debug("Error message received from %s: %s" % (msg['from'], msg.body))
        return
      elif msg['type'] == 'chat':
        if self.message_handler:
          self.message_handler.answer(
            transport = self.chat,
            recipient = msg['from'],
            message = msg.body)
        else:
          self.chat(msg['from'], "Message received sir!")
    except Exception, e:
      log.error("Some error occurred: %s" % e)

  def chat(self, to, body):
    message = domish.Element((None, 'message'))
    message['to'] = to
    message['from'] = self.parent.jid.full()
    message['type'] = 'chat'
    message.addElement('body', content=body)
    self.xmlstream.send(message)
    log.debug(u"Sent %s message (len=%d) to %s: %s" % (message['type'], len(str(message.body)), message['to'], message.body))

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
        elif msg == "$error":
          import pdb
          pdb.set_trace()
        else:
          if session.current_menu and not session.current_menu.is_finished():
            response = handle_session(session, msg)
          else:
            response = "Use $start to create menu"
        if recipient and response:
          transport(recipient, response)
        else:
          log.error("Either recipient (%s) or response (%s) is not valid!" % (recipient, response))
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

