OpenDNA Autobahn-Python REPL
============================
A REPL environment for working with WAMP routers in an interactive fashion built
using the Autobahn-Python library. Throughout this document the TLA APR is used
to refer to the REPL application


Contents
--------
1. Installation
2. Usage

   1. Starting the REPL
   2. Connections
   3. Sessions
   4. Calls and Invocations
   5. Registrations
   6. Publishers and Publications
   7. Subscriptions

3. Extending

   1. PtPython config module
   2. REPL class substitution

5. Roadmap
6. Credits


Installation
------------
``pip install autobahn-python-repl``

APR requires Python 3.6 to run. If you are not using Python
3.6 in your WAMP project then it is recommend you create a Python 3.6 virtual
environment and install the REPL there.


Usage
-----

Starting the REPL
~~~~~~~~~~~~~~~~~
1. Run the ``autobahn_python_repl`` script installed by this package
2. Run ``python -m opendna.autobahn.repl.rpl``

Connections
```````````
Once APR has started you will be presented with a standard PtPython prompt and
environment. In order to begin connecting to a WAMP router enter:

``>>> my_router = connect_to(uri='ws://HOST:PORT', realm='MY_REALM')``

This will create a ``Connection`` instance, assign it to ``my_router`` and
output some text like:

``Generating connection to MY_REALM@ws://HOST:PORT with name g9jZlZeh``

You will see that ``connect_to`` generated an internal name for the connection.
You can access the connection via this internal name by entering:

``>>> connections.g9jZlZeh``

It is also possible to provide a custom internal name for the connection when
you call ``connect_to`` as follows:

``>>> connect_to(uri='ws://HOST:PORT', realm='MY_REALM', name='my_router')``

We can then access the connection by entering:

``>>> connections.my_router``

or

``>>> connections['my_router']``

Note that the ``Connection`` object is not actually a concrete connection to
the WAMP router, it is merely a storage container for connection related
details that is used to create ``Session`` objects which represent actual
connections to the WAMP router.

``connect_to`` accepts the follows arguments:

* ``uri``: Required. A WAMP router URI string
* ``realm``: Optional. A WAMP realm string
* ``extra``: Optional. A dictionary of data to be supplied to the WAMP
  ``ApplicationSession``.``__init__`` method. Not useful unless you are
  working with a custom ``ApplicationSessions`` class. See *Extending* for
  more details on this.
* ``serializer``: Optional. A list of WAMP serializers to use. Serializers must
  implement ``autobahn.wamp.interfaces.ISerializer``
* ``ssl``: Optional. Boolean or ``ssl.SSLContenxt`` instance. Can usually
  be ignored unless you are planning to connect use TLS authentication for a
  ``Session``
* ``proxy``: Optional. A dictionary providing details for a proxy server. Must
  have ``host`` and ``port`` keys
* ``name``: Optional. A name for the connection

Sessions
````````

Once you have a ``Connection`` instance you can use it to open a WAMP session:

``>>> session1 = my_router.session()``

This will create a ``Session`` instance and assign it to ``session1``. It will
also output some text like:

``Generating anonymous session to MY_REALM@ws://HOST:PORT with name bKP5ajz0``

You can access this session via its auto-generated name like so:

``>>> my_router.sessions.bKP5ajz0``

You can also use the array indexing method and can even omit usage of the ``sessions``
attribute on the ``Connection`` instance if you so choose. ``session`` also
accepts a *name* parameter that you can use to avoid using an auto-generated name.

By default calling ``session`` will open an ``Anonymous`` session with the router.

It is also possible to specify the authentication method or methods that will
be used::

  >>> session2 = my_router.session('ticket', authid='your_authid', ticket='YOUR_AUTHENTICATION_TICKET')
  Generating ticket session to MY_REALM@ws://HOST:PORT with name SOME_NAME
  >>> session3 = my_router.session(['ticket', 'anonymous'], authid='your_authid', ticket='YOUR_AUTHENTICATION_TICKET')
  Generating ['ticket', 'anonymous'] session to MY_REALM@ws://HOST:PORT with name bKP5ajz0

*session2* will use WAMP-Ticket authentication only while *session3* will try
WAMP-Ticket first before falling back to WAMP-Anonymous.

While WAMP provides a number a authentication methods, only four of are handled
at the session level (as opposed to the transport level). Calling the ``session``
method with a specific authentication may imply the use of certain additional
parameters. These are detailed below:

* WAMP-Anonymous: No parameters required. Note that ``authid`` will be ignored if it is supplied
* WAMP-Ticket: ``authid`` and ``ticket`` parameters required
* WAMP-CRA: ``authid`` and ``secret`` parameters required
* WAMP-Cryptosign: ``authid`` and ``key`` parameters required. ``key`` needs to be an instance of ``autobahn.wamp.cryptosign.SigningKey``

The ``Connection.session`` method accepts the following arguments:

* ``authmethods``: Optional. String or list of strings. Valid authentication method
  strings are: ``anonymous``, ``ticket``, ``wampcra``, ``cryptosign``, ``cookie`` and ``tls``
* ``authid``: String. Optional for WAMP-Anonymous authentication, required for all other methods
* ``authrole``: String. Optional. Requested role
* ``authextra``: Dictionary. Optional. Data to be passed along to the authenticator. Useful
  for providing additional data to a dynamic authenticator
* ``resumable``: Boolean. Optional. Should the session be resumed later if it disconnects
* ``resume_session``: Integer. Optional. ID of Session to resume
* ``resume_token``: String. Optional. Token for resuming session specified by ``resume_session``

Calls and Invocations
`````````````````````
TBD

Registrations
`````````````
TBD

Publishers and Publications
```````````````````````````
TBD

Subscriptions
`````````````
TBD


Extending
---------
TBD

Roadmap
-------

* Improved UI with custom panes/tabs/views for examining Calls, Invocations,
  Publishers, Publications, Registrations and Subscriptions
* Support usage in other REPLs


Credits
-------

* Autobahn-Python for providing the secret WAMP sauce
* PtPython for providing the secret REPL sauce
* Jedi for providing PtPython with the secret code completion sauce
* PromptToolkit for providing PtPython with the prompt secret sauce

