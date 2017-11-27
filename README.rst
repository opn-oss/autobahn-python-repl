OpenDNA Autobahn-Python REPL
============================
A REPL environment for working with WAMP routers in an interactive fashion built
using the Autobahn-Python library. Throughout this document the TLA APR is used
to refer to the REPL application


Contents
--------
1. `Installation`_
2. `Usage`_

   1. `Starting the REPL`_
   2. `Connections`_
   3. `Sessions`_
   4. `Calls and Invocations`_
   5. `Registrations`_
   6. `Publishers and Publications`_
   7. `Subscriptions`_

3. `Extending`_

   1. `PtPython config module`_
   2. `REPL class substitution`_

5. `Roadmap`_
6. `Credits`_


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
  Generating ['ticket', 'anonymous'] session to MY_REALM@ws://HOST:PORT with name SOME_OTHER_NAME

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
Once you have a ``Session`` instance you can use it to create ``Call`` instance:

``>>> my_call = session1.call('endpoint_uri')``

This will create a ``Call`` instance and assign it to ``my_call``. It will
also output some text like:

``Generating a call to endpoint endpoint_uri with name i9BcEagW``

You can access this call by it's autogenerated name like so:

``session1.calls.i9BcEagW``

You can also use the array indexing method and can also use both attribute
and indexing to access it via the ``call`` method on the ``Session`` instance.
You can also provide a a custom *name* parameter to bypass the use of an autogenerated
name. Furthermore, the ``call`` method accepts any keyword-arguments you can
supply to the `autobahn.wamp.types.CallOptions constructor`_.

.. _autobahn.wamp.types.CallOptions constructor: https://autobahn.readthedocs.io/en/latest/reference/autobahn.wamp.html#autobahn.wamp.types.CallOptions

A ``Call`` instance is itself callable and can be invoked in order to produce an
``Invocation`` instance:

``invocation1 = my_call(True, False, parm3=None, parm4={'something': 'or other'})``

This will create an ``Invocation`` instance, assign it to ``inv1`` and schedule
execution against the ``Session`` instance. The output will be something like::

  Invoking endpoint_uri with name Wax3JdBx
  Invocation of endpoint_uri with name Wax3JdBx starting
  Invocation of endpoint_uri with name Wax3JdBx succeeded

Depending on how long it takes for the remote end-point to execute, the message
indicating success or failure may not appear immediately. You will note that
the ``Invocation`` also receives a auto-generated name which can be used to access
it from the ``Call`` instance like so:

``my_call.invocations.Wax3JdBx``

As expected, array indexing can also be used and the ``.invocations`` component
can be omitted.

The ``Invocation`` instance exposes three important properties that can be
used to access the results of the WAMP Call:

* ``result`` will contain the result of the WAMP Call if it succeeded or ``None`` if it failed or hasn't completed yet
* ``exception`` will contain the result of the WAMP Call if it failed or ``None`` if it failed or hasn't completed yet
* ``progress`` is a list which is used to store progressive results if the
  target WAMP end-point emits them. See https://crossbar.io/docs/Progressive-Call-Results/ for more details on this

Finally, an ``Invocation`` instance is itself callable. Calling an ``Invocation`` will
produce a new ``Invocation`` instance attached to the parent ``Call`` of the called ``Invocation``.
The behaviour of the arguments and keyword arguments when calling an ``Invocation`` is quite specific
and affects the creation of the new ``Invocation`` as follows:

* Positional arguments will replace the corresponding positional arguments from the parent ``Invocation``
  in the new ``Invocation`` unless the positional argument is a reference to the singleton object ``opendna.autobahn.repl.utils.Keep``
  To illustrate this consider the following scenario::

    my_call = session1.call('some_endpoint')
    invocation1 = my_call(1,2,3)
    invocation2 = invocation1(3, Keep, 1)
    invocation3 = my_call(3,2,1)

  In this scenario ``invocation2`` and ``invocation3`` are identical

* If the number of positional arguments supplied is less than was supplied to the parent ``Invocation`` then the
  missing positional arguments will be substituted in from the parent ``Invocation`` as if ``Keep`` had been used in their
  positions

* If the number of position arguments supplied is greater than was supplied to the parent ``Invocation`` then the
  additional positional arguments will be ignored

* Any keyword arguments will replace the corresponding keyword arguments from the parent ``Invocation``::

    my_call = session1.call('some_endpoint')
    invocation1 = my_call(x=True, y=False)
    invocation2 = invocation1(y=True)
    invocation3 = my_call(x=True, y=True)

  In this scenario ``invocation2`` and ``invocation3`` are identical

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

PtPython config module
~~~~~~~~~~~~~~~~~~~~~~
TBD

REPL class substitution
~~~~~~~~~~~~~~~~~~~~~~~
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

