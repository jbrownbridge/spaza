from zope.interface import implements
from getpass import getpass

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker

from django.core.management import setup_environ
from spaza import settings

setup_environ(settings)

import os.path, sys

from ussd.transport.xmpp import XMPPClient

class Options(usage.Options):
  optParameters = [
    ["xmpp-username", "u", None, "XMPP username.", str],
    ["xmpp-password", "p", '', "XMPP password.", str],
    ["xmpp-host", "h", 'talk.google.com', "XMPP host.", str],
    ["xmpp-port", None, 5222, "XMPP host's port.", int],
  ]

class XMPPServiceMaker(object):
  implements(IServiceMaker, IPlugin)
  tapname = "xmpp"
  description = "Run Spaza USSD emulation over XMPP"
  options = Options

  def makeService(self, options):
    if not options['xmpp-password']:
      options['xmpp-password'] = getpass('password for %s: ' % \
        options['xmpp-username'])
    return XMPPClient(
      username=options['xmpp-username'],
      password=options['xmpp-password'],
      host=options['xmpp-host'],
      port=options['xmpp-port'])

service = XMPPServiceMaker()
