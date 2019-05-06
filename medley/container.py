import re
from .errors import FrozenServiceError, UnknownIdentifierError

try:
    from collections.abc import Hashable
except ImportError:
    from collections import Hashable


class MedleyContainer(object):

    def __init__(self, services={}):
        self._values = {}
        self._raw = {}
        self._factories = set()
        self._protected = set()
        self._frozen = set()
        self._keys = set()

        for key, value in services.items():
            self.__setitem__(key, value)

    def service(self, id):
        def decorator(func):
            self.__setitem__(id, func)
        return decorator

    def create_factory(self, id):
        def decorator(func):
            self.__setitem__(id, self.factory(func))
        return decorator

    def extends(self, id):
        def decorator(func):
            self.extend(id, func)
        return decorator

    def match(self, regex):
        matches = set()
        compiled = re.compile(regex)

        for key in self._keys:
            if compiled.match(key):
                matches.add(self.__getitem__(key))

        return matches

    def factory(self, func):
        if not callable(func):
            raise ValueError('Service definition is not a function or callable object.')

        self._factories.add(func)
        return func

    def protect(self, func):
        if not callable(func):
            raise ValueError('Callable is not a function or callable object.')

        self._protected.add(func)
        return func

    def raw(self, id):
        if id not in self._keys:
            raise UnknownIdentifierError('Identifier "{}" is not defined.'.format(id))

        if id in self._raw:
            return self._raw[id]

        return self._values[id]

    def extend(self, id, func):
        if id not in self._keys:
            raise ValueError('Identifier "{}" is not defined.'.format(id))

        if not callable(self._values[id]):
            raise ValueError('Identifier "{}" does not contain an object definition.'.format(id))

        if not callable(func):
            raise ValueError('Extension service definition is not a function or callable object.')

        factory = self._values[id]

        def extended(c):
            return func(factory(c), c)

        if factory in self._factories:
            self._factories.remove(factory)
            self._factories.add(extended)

        self.__setitem__(id, extended)
        return extended

    def keys(self):
        return self._values.keys()

    def register(self, provider, values={}):
        provider.register(self)

        for key, value in values.items():
            self.__setitem__(key, value)

        return self

    def __setitem__(self, id, value):
        if id in self._frozen:
            raise FrozenServiceError('Cannot override service %s' % id)

        self._values[id] = value
        self._keys.add(id)

    def __getitem__(self, id):
        if id not in self._keys:
            raise UnknownIdentifierError('Indentifier %s is not defined' % id)

        if (id in self._raw
                or not isinstance(self._values[id], Hashable)
                or isinstance(self._values[id], bytearray)  # Python 2.7 Fix
                or self._values[id] in self._protected
                or not callable(self._values[id])):
            return self._values[id]

        if self._values[id] in self._factories:
            return self._values[id](self)

        raw = self._values[id]
        val = raw(self)

        self._values[id] = val
        self._raw[id] = raw
        self._frozen.add(id)

        return val

    def __delitem__(self, id):
        if id in self._keys:
            if id in self._values:
                if callable(self._values[id]):
                    self._factories.discard(self._values[id])
                    self._protected.discard(self._values[id])

                del self._values[id]

            if id in self._raw:
                del self._raw[id]

            self._frozen.discard(id)
            self._keys.discard(id)

    def __contains__(self, id):
        return id in self._keys

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return iter(self._values)
