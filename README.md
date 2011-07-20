Installing prerequisites
===========================

Execute the following code to install the prerequisites:

    $ sudo aptitude install -y python-setuptools
    $ sudo easy_install pip
    $ sudo pip install virtualenvwrapper
    ...

Setup virtualenvwrapper
============================

In order to make the most use of virualenvwrapper, ensure the following lines
are at the end of you ~/.bashrc file (~/.profile in Mac):

    export PIP_RESPECT_VIRTUALENV=true
    export WORKON_HOME=$HOME/ve
    source /usr/local/bin/virtualenvwrapper.sh

One quick note about the WORKON_HOME variable - that''s where the virtualenvs 
are going to be stored. Modify that so it fits your system.

Before moving to the next step, make sure your source your new .bashrc 
(.profile on Mac) so all the virtualenvwrapper goodness will be available to 
you.

Getting started
===============

First things first you need to checkout this repo:

    $ git clone git@github.com:jbrownbridge/spaza.git 
    ...

Create a new virtual environment called ""spaza"", activate it and make sure all 
requirements are installed:

    $ mkvirtualenv --no-site-packages spaza
    (spaza) $ pip install -r config/requirements.pip
    ...

Notice how the shell prompt has been updated to have a ""(spaza)"" proceeding 
""$"" - this indicates that the virtual environment named "(spaza)" is active. 
To deactivate it use the following:

    (spaza) $ deactivate
    $
    ...

Likewise to reactivate it to continue development use the following command:

    $ workon spaza
    (spaza) $
    ...

Running Django the server
=========================

To run the server on your local machine on port 8000 use the following command:

    (spaza) $ cd spaza
    (spaza) $ python manage.py runserver
    ...

I suggest instead of using python to run the server directory, consider using
ipython for the advanced debugging features it provides:

    (spaza) $ cd spaza
    (spaza) $ ipython manage.py runserver
    ...

You can now view your server by opening http://127.0.0.1:8000 in your browser.

Running XMPP Server
=========================
1. Create virtual environment: mkvirtualenv --no-site-packages spaza
3. Install requirements: pip install -r config/requirements.pip
4. Start twisted server: twistd --pidfile=tmp/twistd.xmpp.pid -n xmpp --xmpp-username=ussd2@valency.co.za
5. Enter password when prompted: easypass
6. Add ussd2@valency.co.za as jabber contact in gtalk/etc.
7. Send $start and follow menus

Using USSD
==================
1. Dial *120*364*777*3532893#
2. If this doesn''t work contact Jason to update valency server.
