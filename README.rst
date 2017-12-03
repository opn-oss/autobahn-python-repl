OpenDNA Autobahn-Python REPL
============================
A REPL environment for working with WAMP routers in an interactive fashion built
using the Autobahn-Python library.


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

4. `REPL API`_
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
2. Run ``python -m opendna.autobahn.repl.repl``

Connections
```````````
Once the REPL has started you will be presented with a standard PtPython prompt
and environment. In order to begin connecting to a WAMP router enter::

  >>> my_connection = connect_to(uri='ws://HOST:PORT', realm='MY_REALM')
  Generating connection to MY_REALM@ws://HOST:PORT with name g9jZlZeh

You will see that ``connect_to`` generated an internal name for the connection.
You can access the connection via this internal name by entering::

  >>> connections.g9jZlZeh
  <opendna.autobahn.repl.connections.Connection object at 0x6fc2901ab0f0>

It is also possible to provide a custom internal name for the connection when
you call ``connect_to`` as follows::

  >>> connect_to(uri='ws://HOST:PORT', realm='MY_REALM', name='my_connection')
  Generating connection to MY_REALM@ws://HOST:PORT with name my_connection

You can now access the connection by entering::

  >>> connections.my_connection
  <opendna.autobahn.repl.connections.Connection object at 0x2ac690dab0f0>
  >>> connections['my_connection']
  <opendna.autobahn.repl.connections.Connection object at 0x2ac690dab0f0>

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
Once you have a ``Connection`` instance you can use it to create a ``Session``
instance, opening a WAMP session in the process::

  >>> my_session = my_connection.session()
  Generating anonymous session to MY_REALM@ws://HOST:PORT with name bKP5ajz0

You can access this session via its auto-generated name like so::

  >>> my_connection.sessions.bKP5ajz0
  <opendna.autobahn.repl.sessions.Session object at 0x14c2b01a40fd>
  >>> my_connection.sessions['bKP5ajz0']
  <opendna.autobahn.repl.sessions.Session object at 0x14c2b01a40fd>

``session`` also accepts a *name* parameter that you can use to avoid using an
auto-generated name.

By default calling ``session`` will open a *WAMP-Anonymous* session with the router.

It is also possible to specify the authentication method or methods that will
be used::

  >>> ticket_session = my_connection.session('ticket', authid='your_authid', ticket='YOUR_AUTHENTICATION_TICKET')
  Generating ticket session to MY_REALM@ws://HOST:PORT with name SOME_NAME
  >>> mixed_session = my_connection.session(['ticket', 'anonymous'], authid='your_authid', ticket='YOUR_AUTHENTICATION_TICKET')
  Generating ['ticket', 'anonymous'] session to MY_REALM@ws://HOST:PORT with name SOME_OTHER_NAME

*ticket_session* will use WAMP-Ticket authentication only while *mixed_session*
will try WAMP-Ticket first before falling back to WAMP-Anonymous.

While WAMP provides a number a authentication methods, only four of are handled
at the session level (as opposed to the transport level). Calling the ``session``
method with a specific authentication method may imply the use of certain additional
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
In order to perform WAMP RPC calls you need to create a ``Call`` instance. This is
done using a ``Session`` instance::

  >>> my_call = my_session.call('endpoint_uri')
  Generating a call to endpoint endpoint_uri with name i9BcEagW

You can access this call by it's autogenerated name like so::

  >>> my_session.calls.i9BcEagW
  <opendna.autobahn.repl.rpc.Call object at 0xa452bd1a6f2>
  >>> my_session.calls['i9BcEagW']
  <opendna.autobahn.repl.rpc.Call object at 0xa452bd1a6f2>

``call`` also accepts a custom *name* parameter to bypass the use of an autogenerated
name. Furthermore, the ``call`` method accepts any keyword-arguments you can
supply to the `autobahn.wamp.types.CallOptions constructor`_.

.. _autobahn.wamp.types.CallOptions constructor: https://autobahn.readthedocs.io/en/latest/reference/autobahn.wamp.html#autobahn.wamp.types.CallOptions

A ``Call`` instance is itself callable and can be invoked in order to produce an
``Invocation`` instance. Creating an ``Invocation`` initiates the process of
sending the WAMP RPC call using the ``Session`` instance associated with the
``Call`` instance that is the parent of the ``Invocation``::

  >>> my_invocation = my_call(True, False, parm3=None, parm4={'something': 'or other'})
  Invoking endpoint_uri with name Wax3JdBx
  Invocation of endpoint_uri with name Wax3JdBx starting
  Invocation of endpoint_uri with name Wax3JdBx succeeded

Depending on how long it takes for the remote end-point to execute, the message
indicating success or failure may not appear immediately. You will note that
the ``Invocation`` also receives a auto-generated name which can be used to access
it from the ``Call`` instance like so::

  >>> my_call.invocations.Wax3JdBx
  <opendna.autobahn.repl.rpc.Invocation object at 0xd456bc1aef5>
  >>> my_call.invocations['Wax3JdBx']
  <opendna.autobahn.repl.rpc.Invocation object at 0xd456bc1aef5>


The ``Invocation`` instance exposes three important properties that can be
used to access the results of the WAMP Call:

* ``result`` will contain the result of the WAMP Call if it succeeded or ``None`` if it failed or hasn't completed yet
* ``exception`` will contain the result of the WAMP Call if it failed or ``None`` if it succeeded or hasn't completed yet
* ``progress`` is a list which is used to store progressive results if the
  target WAMP end-point emits them. See https://crossbar.io/docs/Progressive-Call-Results/ for more details on this

Finally, an ``Invocation`` instance is itself callable. Calling an ``Invocation`` will
produce a new ``Invocation`` instance attached to the parent ``Call`` of the called ``Invocation``.
The behaviour of the arguments and keyword arguments when calling an ``Invocation`` is quite specific
and affects the creation of the new ``Invocation`` as follows:

* Positional arguments will replace the corresponding positional arguments from the parent ``Invocation``
  in the new ``Invocation`` unless the positional argument is a reference to the singleton object ``opendna.autobahn.repl.utils.Keep``
  To illustrate this consider the following input scenario::

    >>>  my_call = my_session.call('some_endpoint')
    >>>  invocation1 = my_call(1,2,3)
    >>>  invocation2 = invocation1(3, Keep, 1)
    >>>  invocation3 = my_call(3,2,1)

  In this scenario ``invocation2`` and ``invocation3`` are identical

* If the number of positional arguments supplied is less than was supplied to the parent ``Invocation`` then the
  missing positional arguments will be substituted in from the parent ``Invocation`` as if ``Keep`` had been used in their
  positions

* If the number of position arguments supplied is greater than was supplied to the parent ``Invocation`` then the
  additional positional arguments will be ignored

* Any keyword arguments will replace the corresponding keyword arguments from the parent ``Invocation``::

    >>> my_call = my_session.call('some_endpoint')
    >>> invocation1 = my_call(x=True, y=False)
    >>> invocation2 = invocation1(y=True)
    >>> invocation3 = my_call(x=True, y=True)

  In this scenario ``invocation2`` and ``invocation3`` are identical

Registrations
`````````````
In order to handle calls to WAMP RPC end-points you need to create a
``Registration`` instance::

  >>> my_registration = my_session.register('endpoint_uri')
  Generating registration for endpoint_uri with name Rx3mmt2e
  Registration of endpoint_uri with name Rx3mmt2e starting
  Registration of endpoint_uri with name Rx3mmt2e succeeded

You can access this registration by it's autogenerated name like so::

  >>> my_session.registrations.Rx3mmt2e
  <opendna.autobahn.repl.rpc.Registration object at 0x7fc89015b0f0>
  >>> my_session.registrations['Rx3mmt2e']
  <opendna.autobahn.repl.rpc.Registration object at 0x7fc89015b0f0>

You can also provide a a custom *name* parameter to bypass the use of an autogenerated
name. Furthermore, the ``register`` method accepts any keyword-arguments you can
supply to the `autobahn.wamp.types.RegisterOptions constructor`_.

.. _autobahn.wamp.types.RegisterOptions constructor: https://autobahn.readthedocs.io/en/latest/reference/autobahn.wamp.html#autobahn.wamp.types.RegisterOptions

Once a registration has succeeded it is available for calling as described in
the `Calls and Invocations`_ section. By default the ``Registration`` class
provides a default handler for incoming calls which records the input parameters
along with the date and time of the call using a a ``Registration..Hit`` instance.
This ``Hit`` is a ``namedtuple`` providing three attributes: *timestamp*, *args*
and *kwargs*. When the registration is the target of a call the console will output text like:

``End-point endpoint_uri named Rx3mmt2e hit at 2017-12-01 22:04:10.030438. Hit named jqD8TxFp stored``

Hits stored on a registration can be accessed using either the auto-generated name
or via a numeric index (hits are stored in the order they are received)::

  >>> my_registration.hits[0]
  Hit(timestamp=datetime.datetime(2017, 12, 1, 22, 4, 10, 30438), args=(1, 2, 3, False, True, {}), kwargs={'x': None})
  >>> my_registration.hits.jqD8TxFp
  Hit(timestamp=datetime.datetime(2017, 12, 1, 22, 4, 10, 30438), args=(1, 2, 3, False, True, {}), kwargs={'x': None})

When creating a ``Registration`` it is also possible to specify a custom handler
which is used in addition to the default handler for incoming calls. This custom
handler may be either a standard function or an async function and is called
after the hit is stored by the ``Registration`` instance. Additionally, the result
of the custom handler will be returned to the caller (the default handler will return
``None`` in the event that no custom handler is supplied)::

  >>> import asyncio
  >>> async def test(*args, **kwargs):
          await asyncio.sleep(5)
          print(args, kwargs)
          return True
  >>> my_registration = my_session.register('endpoint_uri', test)
  Generating registration for endpoint_uri with name Rx3mmt2e
  Registration of endpoint_uri with name Rx3mmt2e starting
  Registration of endpoint_uri with name Rx3mmt2e succeeded
  >>> invocation = my_session.call('endpoint_uri')(1,2,3,False,True,{},x=None)
  Generating call to endpoint_uri with name shejtoeU
  Invoking endpoint_uri with name dgSHC77i
  Invocation of endpoint_uri with name dgSHC77i starting
  End-point endpoint_uri named Rx3mmt2e hit at 2017-12-01 22:04:10.030438. Hit named jqD8TxFp stored
  (1, 2, 3, False, True, {}) {'x': None}
  Invocation of endpoint_uri with name dgSHC77i succeeded
  >>> invocation.result
  True

It is also possible to deregister an existing registration::

  >>> my_registration.deregister()
  Deregistration of endpoint_uri with name Rx3mmt2e starting
  Deregistration of endpoint_uri with name Rx3mmt2e succeeded

Publishers and Publications
```````````````````````````
In order to emit WAMP PubSub events you need to create a ``Publisher`` instance::

  >>> my_publisher = my_session.publish('topic_uri')
  Generating publisher for topic_uri with name YunLGYwr

You can access this publisher by it's autogenerated name like so::

  >>> my_session.publishers.YunLGYwr
  <opendna.autobahn.repl.pubsub.Publisher object at 0x7fe1ec20a160>
  >>> my_session.publishers['YunLGYwr']
  <opendna.autobahn.repl.pubsub.Publisher object at 0x7fe1ec20a160>

You can also provide a a custom *name* parameter to bypass the use of an autogenerated
name. Furthermore, the ``publish`` method accepts any keyword-arguments you can
supply to the `autobahn.wamp.types.PublishOptions constructor`_.

.. _autobahn.wamp.types.PublishOptions constructor: https://autobahn.readthedocs.io/en/latest/reference/autobahn.wamp.html#autobahn.wamp.types.PublishOptions

A ``Publisher`` instance is itself callable and can be invoked in order to produce an
``Publication`` instance. Creating a ``Publication`` initiates the process of
sending the WAMP PubSub event using the ``Session`` instance associated with the
``Publisher`` instance that is the parent of the ``Publication``::

  >>> my_publication = my_publisher(a=True, b=False)
  Publication to topic_uri with name CHrYRIn8 starting
  Publication to topic_uri with name CHrYRIn8 succeeded

You will note that the ``Publication`` also receives a auto-generated name which
can be used to access it from the parent ``Publisher`` instance like so::

  >>> my_publisher.publications.CHrYRIn8
  <opendna.autobahn.repl.pubsub.Publication object at 0x7fe1f496a5c0>
  >>> my_publisher.publications['CHrYRIn8']
  <opendna.autobahn.repl.pubsub.Publication object at 0x7fe1f496a5c0>

The ``Publication`` instance exposes two important properties that can be
used to access the results of the WAMP PubSub event emission:

* ``result`` will contain the result of the WAMP PubSub event emission if the ``acknowledge`` boolean
  parameter supplied to the ``publish`` was set to ``True``. In all other instances it will contain ``None``
* ``exception`` will contain the exception result of the WAMP PubSub event emission if it failed or ``None``
  if no failure was detected

Finally, a ``Publication`` instance is itself callable. Calling a ``Publication`` will
produce a new ``Publication`` instance attached to the parent ``Publisher`` of the
called ``Publication``. The behaviour of the arguments and keyword arguments when
calling a ``Publication`` is quite specific and affects the creation of the new
``Publication`` as follows:

* Positional arguments will replace the corresponding positional arguments from the parent ``Publication``
  in the new ``Publication`` unless the positional argument is a reference to the singleton object ``opendna.autobahn.repl.utils.Keep``
  To illustrate this consider the following input scenario::

    >>>  my_publisher = my_session.publish('some_topic')
    >>>  publication1 = my_publisher(1,2,3)
    >>>  publication2 = publication1(3, Keep, 1)
    >>>  publication3 = my_publisher(3,2,1)

  In this scenario ``publication2`` and ``publication3`` are identical

* If the number of positional arguments supplied is less than was supplied to the parent ``Publication`` then the
  missing positional arguments will be substituted in from the parent ``Publication`` as if ``Keep`` had been used in their
  positions

* If the number of position arguments supplied is greater than was supplied to the parent ``Publication`` then the
  additional positional arguments will be ignored

* Any keyword arguments will replace the corresponding keyword arguments from the parent ``Publication``::

    >>> my_publisher = my_session.publish('some_topic')
    >>> publication1 = my_publisher(x=True, y=False)
    >>> publication2 = publication1(y=True)
    >>> publication3 = my_publisher(x=True, y=True)

  In this scenario ``publication2`` and ``publication3`` are identical

Subscriptions
`````````````
In order to subscribe to WAMP PubSub topics you need to create a ``Subscription`` instance::

  >>> my_subscription = my_session.subscribe('topic_uri')
  Generating subscription for topic_uri with name bIMq6XcO
  Subscription to topic_uri with name bIMq6XcO starting
  Subscription to topic_uri with name bIMq6XcO succeeded

You can access this subscription by it's autogenerated name like so::

  >>> my_session.subscriptions.bIMq6XcO
  <opendna.autobahn.repl.pubsub.Subscription object at 0x7fe1f5f9aef0>
  >>> my_session.subscriptions['bIMq6XcO']
  <opendna.autobahn.repl.pubsub.Subscription object at 0x7fe1f5f9aef0>

You can also provide a a custom *name* parameter to bypass the use of an autogenerated
name. Furthermore, the ``subscribe`` method accepts any keyword-arguments you can
supply to the `autobahn.wamp.types.SubscribeOptions constructor`_.

.. _autobahn.wamp.types.SubscribeOptions constructor: https://autobahn.readthedocs.io/en/latest/reference/autobahn.wamp.html#autobahn.wamp.types.SubscribeOptions

Once a subscription has succeeded it will be notified of WAMP PubSub events
emitted as described in the `Publishers and Publications`_ section. Note, however,
that by default a subscription to a topic will only receive events emitted by
other sessions. The *exclude_me* parameter for the ``Publisher`` must be set to
``True`` if you wish to test publication and subscription to a given topic within
a single ``Session``.

The ``Subscription`` class provides a default handler for incoming events which
records the input parameters along with the date and time of the call using a
``Subscription.Hit`` instance. This ``Event`` is a ``namedtuple`` providing three
attributes: *timestamp*, *args* and *kwargs*. When the subscription receives an
event the console will output text like:

``Event named s3X0Sbhc received at 2017-12-03 21:59:55.437068 on topic topic_uri named bIMq6XcO``

Events stored on a subscription can be accessed using either the auto-generated name
or via a numeric index (hits are stored in the order they are received)::

  >>> my_subscription.events[0]
  Event(timestamp=datetime.datetime(2017, 12, 1, 22, 4, 10, 30438), args=(1, 2, 3, False, True, {}), kwargs={'x': None})
  >>> my_subscription.events.jqD8TxFp
  Event(timestamp=datetime.datetime(2017, 12, 1, 22, 4, 10, 30438), args=(1, 2, 3, False, True, {}), kwargs={'x': None})

When creating a ``Subscription`` it is also possible to specify a custom handler
which is used in addition to the default handler for incoming events. This custom
handler may be either a standard function or an async function and is called
after the event is stored by the ``Subscription`` instance::

  >>> async def test(*args, **kwargs):
          print(args, kwargs)
  >>> my_subscription = my_session.subscribe('topic_uri', test)
  Generating subscription for topic_uri with name bIMq6XcO
  Subscription to topic_uri with name bIMq6XcO starting
  Subscription to topic_uri with name bIMq6XcO succeeded
  >>> publication = my_session.publish('topic_uri', exclude_me=False)(1,2,3,False,True,{},x=None)
  Generating publisher for topic_uri with name VVjZjvF5
  Publication to topic_uri with name sjfuAGSm starting
  Publication to topic_uri with name sjfuAGSm succeeded
  Event named ZbbzBrxJ received at 2017-12-03 22:18:10.383218 on topic topic_uri named bIMq6XcO
  (1, 2, 3, False, True, {}) {'x': None}
  >>> my_subscription.events.ZbbzBrxJ
  Event(timestamp=datetime.datetime(2017, 12, 3, 22, 18, 10, 383218), args=(1, 2, 3, False, True, {}), kwargs={'x': None})

It is also possible to unsubscribe from a topic::

  >>> my_subscription.unsubscribe()
  Unsubscription from topic_uri with name bIMq6XcO starting
  Unsubscription from topic_uri with name bIMq6XcO succeeded

Extending
---------
TBD

PtPython config module
~~~~~~~~~~~~~~~~~~~~~~
TBD

REPL class substitution
~~~~~~~~~~~~~~~~~~~~~~~
TBD


REPL API
--------
TBD


Roadmap
-------

* Improved UI with custom panes/tabs/views for examining Calls, Invocations,
  Publishers, Publications, Registrations and Subscriptions
* ``deregister``/``Unsubscribe`` should clean up the ``Registration``/``Subscription`` instance
* Support usage in other REPLs
* You tell me!


Credits
-------

* Autobahn-Python for providing the secret WAMP sauce
* PtPython for providing the secret REPL sauce
* Jedi for providing PtPython with the secret code completion sauce
* PromptToolkit for providing PtPython with the prompt secret sauce

