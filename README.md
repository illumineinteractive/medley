Medley is a simple, lightweight Dependency Injection Container for Python, inspired by [Pimple](https://github.com/silexphp/Pimple).


Requirements
------------
Medley requires Python >=2.7 or Python >=3.2

[![Build Status](https://travis-ci.org/illumine-interactive/medley.svg?branch=master)](https://travis-ci.org/illumine-interactive/medley)


Installation
------------
Install Medley using pip

```bash
    $ pip install medley
```

Usage
-----

Build your container by creating a ``MedleyContainer`` instance:

```python

    from medley import MedleyContainer

    container = MedleyContainer()
```

Medley manages two different kind of data: **services** and **parameters**.


Defining Services
-----------------

A service is an object that does something as part of a larger system. Examples
of services: a database connection, a templating engine, or a mailer. Almost
any **global** object can be a service.

Services are defined by **functions and lambdas** that return an instance of an
object:

Example using **lambdas**:

```python

    # define some services
    container['session_storage'] = lambda c: SessionStorage('SESSION_ID')

    container['session'] = lambda c: Session(c['session_storage'])
```

Notice that service definition functions do require the container argument.
Lambdas must have access to the current container instance, allowing references
to other services or parameters.

A **service decorator** is also available to wrap defined functions as a service

```python

    @container.service('session_storage')
    def session_storage(c):
        return SessionStorage('SESSION_ID')

    @container.service('session')
    def session(c):
        return Session(c['session_storage'])
```


Objects are **lazy-loaded**, so the order in which you define services
does not matter.

Getting a defined service is easy:

```python

    session = container['session']

    # the above call is roughly equivalent to the following code:
    # storage = SessionStorage('SESSION_ID')
    # session = Session(storage)
```

Defining Factory Services
-------------------------

By default, each time you get a service, Medley returns the **same instance**
of it. If you want a different instance to be returned for all calls, wrap your
anonymous function with the ``factory()`` method

```python

    container['session'] = container.factory(lambda c: Session(c['session_storage']))

    # you may also use a decorator

    @container.create_factory('session')
    def session(c):
        return Session(c['session_storage'])
```

Now, each call to ``container['session']`` returns a new instance of the
session.


Defining Parameters
-------------------

Defining a parameter allows to ease the configuration of your container from
the outside and to store global values:

``` python

    # define some parameters
    container['cookie_name'] = 'SESSION_ID';
    container['session_storage_class'] = 'SessionStorage';
```

If you change the ``session_storage`` service definition like below:


```python

    container['session_storage'] = lambda c: c['session_storage_class'](c['cookie_name'])
```

You can now easily change the cookie name by overriding the
``cookie_name`` parameter instead of redefining the service
definition.


Protecting Parameters
---------------------

Because Medley sees lambdas as service definitions, you need to
wrap lambdas with the ``protect()`` method to store them as
parameters:

``` python

    from random import random

    container['random_func'] = container.protect(lambda: random())
```

Modifying Services after Definition
-----------------------------------

In some cases you may want to modify a service definition after it has been
defined. You can use the ``extend()`` method to define additional code to be
run on your service just after it is created:

```python

    container['session_storage'] = lambda c: c['session_storage_class'](c['cookie_name'])

    container.extend('session_storage' lambda storage, c: storage.some_call()
```

The first argument of the lambda is the name of the service to extend, the
second a function that gets access to the object instance and the container.

The available **extends** decorator is usually more user-friendly when extending
definitions, particularly when a service needs to be modified and returned

```python

    @container.service('session_storage')
    def session_storage(c):
        return c['session_storage_class'](c['cookie_name'])

    @container.extends('session_storage')
    def extended_session_storage(storage, c):
        storage.some_call()
        return storage
```

Extending a Container
---------------------

You can build a set of libraries with Medley using the Providers. You might want
to reuse some services from one project to the next one; package your services
into a **provider** by implementing ``medley.ServiceProviderInterface``:

```python

    from medley import MedleyContainer, ServiceProviderInterface

    class FooProvider(ServiceProviderInterface):

        def register(container: MedleyContainer):
            # register some services and parameters on container
            container['foo'] = lambda c: return 'bar'
```

Then, register the provider on a MedleyContainer:

```python

    container.register(FooProvider())
```


Fetching the Service Creation Function
--------------------------------------

When you access an object via ```container['some_id']```, Medley automatically
calls the function that you defined, which creates the service object for you.
If you want to get raw access to this function, you can use the ``raw()``
method:

```python

    container['session'] = lambda c: Session(c['session_storage'])

    session_function = container.raw('session')
```
