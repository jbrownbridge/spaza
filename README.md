Installing prerequisites
=======================

Execute the following code to install the prerequisites:

    $ sudo aptitude install -y python-setuptools
    $ sudo easy_install pip
    ...

Getting started
===============

First things first you need to checkout this repo:

    $ git clone git@github.com:jbrownbridge/spaza.git 
    ...

Create a new virtual environment called "ve", activate it and make sure all 
requirements are installed:

    $ virtualenv --no-site-packages ve/
    $ source ve/bin/activate
    (ve) $ pip install -r config/requirements.pip
    ...

Notice how the shell prompt has been updated to have a "(ve)" proceeding "$" - 
this indicates that the virtual environment named "(ve)" is active. To deactivate
it use the following:

    (ve) $ source ve/bin/activate
    $
    ...

Likewise to reactivate it to continue development use exactly the same command:

    $ source ve/bin/activate
    (ve) $
    ...

Running Django the server
=========================

To run the server on your local machine on port 8000 use the following command:

    (ve) $ cd spaza
    (ve) $ python manage.py runserver
    ...

I suggest instead of using python to run the server directory, consider using
ipython for the advanced debugging features it provides:

    (ve) $ cd spaza
    (ve) $ ipython manage.py runserver
    ...

You can now view your server by opening http://127.0.0.1:8000 in your browser.

Running XMPP Server
=========================
1. Create virtual environment: virtualenv --no-site-packages ve/
2. Activate it source: ve/bin/activate
3. Install requirements: pip install -r config/requirements.pip
4. Start twisted server: twistd --pidfile=tmp/twistd.xmpp.pid -n xmpp --xmpp-username=ussd2@valency.co.za
5. Enter password when prompted: easypass
6. Add ussd2@valency.co.za as jabber contact in gtalk/etc.
7. Send $start and follow menus

Using USSD
==================
1. Dial *120*364*777*3532893#
2. If this doesn't work contact Jason to update valency server.
