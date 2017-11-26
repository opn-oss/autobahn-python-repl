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

      1. ``connect_to``
      2. ``connections``

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


Sessions
````````


Extending
---------


Roadmap
-------


Credits
-------
PtPython for providing the secret REPL sauce
Jedi for providing PtPython with the secret code completion sauce
PromptToolkit for providing PtPython with the prompt secret sauce
