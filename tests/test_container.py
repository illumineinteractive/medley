import unittest
import types
from mock import Mock, MagicMock, patch
from medley import MedleyContainer


class MedleyContainerTest(unittest.TestCase):

    def setUp(self):
        self.foo = Mock(return_value='foo')
        self.bar = Mock(return_value='bar')
        self.baz = Mock(return_value='baz')
        self.bat = Mock(return_value='bat')

    def test_constructor_loads_default_values(self):
        c = MedleyContainer()

        self.assertEqual(c._values, {})
        self.assertEqual(c._raw, {})
        self.assertEqual(c._factories, set())
        self.assertEqual(c._protected, set())
        self.assertEqual(c._frozen, set())
        self.assertEqual(c._keys, set())

    def test_constructor_calls_set_multiple_times_when_object_is_provided(self):
        with patch.object(MedleyContainer, '__setitem__'):
            c = MedleyContainer({
                'foo': lambda c: None,
                'bar': lambda c: None,
                'baz': lambda c: None
            })

            self.assertEqual(3, c.__setitem__.call_count)

    def test_service_decorator_calls_setitem(self):
        c = MedleyContainer()
        c.__setitem__ = Mock()

        @c.service('foo')
        def foo(c):
            return 'bar'

        c.__setitem__.assert_called_once()

    def test_create_factory_decorator_calls_factory(self):
        c = MedleyContainer()
        c.factory = Mock()

        @c.create_factory('foo')
        def foo(c):
            return 'bar'

        c.factory.assert_called_once()

    def test_create_extends_decorator_calls_extend(self):
        c = MedleyContainer()
        c.extend = Mock()

        @c.extends('foo')
        def foo(c):
            return 'bar'

        c.extend.assert_called_once()

    def test_setitem_access(self):
        with patch.object(MedleyContainer, '__setitem__') as setitem:
            c = MedleyContainer()

            c['foo'] = self.foo
            setitem.assert_called_with('foo', self.foo)

            c['@foo'] = self.foo
            setitem.assert_called_with('@foo', self.foo)

            c['$foo'] = self.foo
            setitem.assert_called_with('$foo', self.foo)

            c['#foo'] = self.foo
            setitem.assert_called_with('#foo', self.foo)

            c['bar'] = self.bar
            setitem.assert_called_with('bar', self.bar)

            c['_baz'] = self.baz
            setitem.assert_called_with('_baz', self.baz)

    def test_multi_dot_setitem_access(self):
        with patch.object(MedleyContainer, '__setitem__') as setitem:
            c = MedleyContainer()

            c['foo.bar'] = self.foo
            setitem.assert_called_with('foo.bar', self.foo)

            c['baz.bat'] = self.baz
            setitem.assert_called_with('baz.bat', self.baz)

    def test_getitem_access(self):
        def call_fake(id):
            values = {
                'foo': self.foo,
                '@foo': self.foo,
                '#foo': self.foo,
                '$foo': self.foo,
                'bar': self.bar,
                'baz': self.baz,
                'bat.ban': self.bat
            }

            return values[id]

        with patch.object(MedleyContainer, '__getitem__', wraps=call_fake) as getitem:
            c = MedleyContainer()

            self.assertEqual(c['foo'], self.foo)
            getitem.assert_called_with('foo')

            self.assertEqual(c['@foo'], self.foo)
            getitem.assert_called_with('@foo')

            self.assertEqual(c['#foo'], self.foo)
            getitem.assert_called_with('#foo')

            self.assertEqual(c['$foo'], self.foo)
            getitem.assert_called_with('$foo')

            self.assertEqual(c['bar'], self.bar)
            getitem.assert_called_with('bar')

            self.assertEqual(c['baz'], self.baz)
            getitem.assert_called_with('baz')

            self.assertEqual(c['bat.ban'], self.bat)
            getitem.assert_called_with('bat.ban')

    def test_throws_error_on_invalid_id(self):
        c = MedleyContainer()

        with self.assertRaises(Exception):
            c['foo']

        with self.assertRaises(Exception):
            c['bar']

        with self.assertRaises(Exception):
            c['baz']

    def test_in_operator(self):
        def call_fake(id):
            values = {
                'foo': self.foo,
                '@foo': self.foo,
                '#foo': self.foo,
                '$foo': self.foo,
                'bar': self.bar,
                'baz': self.baz,
                'bat.ban': self.bat
            }

            return id in values

        with patch.object(MedleyContainer, '__contains__', wraps=call_fake) as contains:
            c = MedleyContainer()

            self.assertEqual('foo' in c, True)
            contains.assert_called_with('foo')

            self.assertEqual('@foo' in c, True)
            contains.assert_called_with('@foo')

            self.assertEqual('#foo' in c, True)
            contains.assert_called_with('#foo')

            self.assertEqual('$foo' in c, True)
            contains.assert_called_with('$foo')

            self.assertEqual('bar' in c, True)
            contains.assert_called_with('bar')

            self.assertEqual('baz' in c, True)
            contains.assert_called_with('baz')

            self.assertEqual('bat.ban' in c, True)
            contains.assert_called_with('bat.ban')

            self.assertEqual('fail' in c, False)
            contains.assert_called_with('fail')

    def test_del_operator(self):
        with patch.object(MedleyContainer, '__delitem__') as delitem:
            c = MedleyContainer()

            del c['foo']
            delitem.assert_called_with('foo')

            del c['bar']
            delitem.assert_called_with('bar')

            del c['baz']
            delitem.assert_called_with('baz')

    def test_match_returns_matched_functions_by_key_name(self):
        c = MedleyContainer()
        c._keys = set(['foo', 'bar', 'baz'])

        def call_fake(id):
            values = {
                'foo': self.foo,
                'bar': self.bar,
                'baz': self.baz
            }

            return values[id]

        with patch.object(MedleyContainer, '__getitem__', wraps=call_fake) as getitem:
            result = c.match("foo")
            getitem.assert_called_with('foo')

            self.assertEqual(len(result), 1)
            self.assertEqual(result.pop(), self.foo)

            result = c.match("(foo|bar)")
            self.assertEqual(len(result), 2)
            self.assertEqual(self.foo in result, True)
            self.assertEqual(self.bar in result, True)

            result = c.match("(foo|bar|baz)")
            self.assertEqual(len(result), 3)
            self.assertEqual(self.foo in result, True)
            self.assertEqual(self.bar in result, True)
            self.assertEqual(self.baz in result, True)
            self.assertEqual(self.bat in result, False)

            result = c.match("bat")
            self.assertEqual(len(result), 0)

    def test_factory_throws_error_if_arg_not_function(self):
        c = MedleyContainer()

        with self.assertRaises(Exception):
            c.factory('foo')

        with self.assertRaises(Exception):
            c.factory(False)

        with self.assertRaises(Exception):
            c.factory(r'match')

        with self.assertRaises(Exception):
            c.factory(0xf)

    def test_factory_adds_factory_function_to_factories_attr(self):
        c = MedleyContainer()
        factories = set()

        with patch.object(c, '_factories', wraps=factories):
            c.factory(self.foo)
            c._factories.add.assert_called_with(self.foo)

            c.factory(self.bar)
            c._factories.add.assert_called_with(self.bar)

            c.factory(self.baz)
            c._factories.add.assert_called_with(self.baz)

            self.assertEqual(c._factories.add.call_count, 3)

    def test_factory_prevents_duplicates(self):
        c = MedleyContainer()
        factories = set()

        with patch.object(c, '_factories', wraps=factories):
            c.factory(self.foo)
            c._factories.add.assert_called_with(self.foo)

            c.factory(self.foo)
            c._factories.add.assert_called_with(self.foo)

            c.factory(self.foo)
            c._factories.add.assert_called_with(self.foo)

            self.assertEqual(c._factories.add.call_count, 3)
            self.assertEqual(len(factories), 1)

    def test_raw_throws_error_when_service_id_does_not_exist(self):
        c = MedleyContainer()
        c._keys = Mock(__contains__=Mock(return_value=False))

        with self.assertRaises(Exception):
            c.raw('foo')

    def test_raw_returns_function_when_exists(self):
        c = MedleyContainer()
        c._keys = Mock()
        c._keys.__contains__ = Mock(return_value=True)
        c._raw = {'foo': self.foo}

        self.assertEqual(c.raw('foo'), self.foo)

    def test_raw_returns_raw_function_from_values_attr_when_it_does_not_exist_in_raw_attr(self):
        c = MedleyContainer()
        c._keys = Mock()
        c._keys.__contains__ = Mock(return_value=True)
        c._raw = Mock()
        c._raw.__contains__ = Mock(return_value=False)
        c._values = {'foo': self.foo}

        self.assertEqual(c.raw('foo'), self.foo)

        c._keys.__contains__.assert_called_with('foo')
        c._raw.__contains__.assert_called_with('foo')

    def test_extend_throws_error_when_service_id_does_not_exist(self):
        c = MedleyContainer()
        c._keys = Mock()
        c._keys.__contains__ = Mock(return_value=False)

        with self.assertRaises(Exception):
            c.extend('foo', self.foo)

    def test_extend_throws_error_if_service_id_is_not_function_def(self):
        c = MedleyContainer()
        c._values = {'foo': 'bar'}

        with self.assertRaises(Exception):
            c.extend('foo', self.foo)

    def test_extend_throws_error_if_second_argument_is_not_function_def(self):
        c = MedleyContainer()

        with self.assertRaises(Exception):
            c.extend('foo', 'bar')

    def test_extends_wraps_function_and_calls_setitem(self):
        c = MedleyContainer()
        c._keys = set(['foo'])
        c._values = {'foo': self.foo}

        with patch.object(MedleyContainer, '__setitem__', wraps=c.__setitem__) as setitem:
            result = c.extend('foo', self.bar)
            self.assertEqual(type(result), types.FunctionType)
            self.assertEqual(c['foo'], result(c))
            setitem.assert_called_once()

    def test_extends_adds_wrapped_function_to_factories_when_exists(self):
        c = MedleyContainer()
        c._keys = set(['foo'])
        c._values = {'foo': self.foo}
        factories = set([self.foo])

        with patch.object(c, '_factories') as f:
            f.__contains__.side_effect = factories.__contains__
            f.add.side_effect = factories.add
            f.remove.side_effect = factories.remove

            c.extend('foo', self.bar)
            f.__contains__.assert_called_with(self.foo)
            f.remove.assert_called_once()
            f.add.assert_called_once()

    def test_keys_returns_valid_list_of_keys(self):
        c = MedleyContainer()
        c._values = {
            'foo': self.foo,
            'bar': self.bar,
            'baz': self.baz
        }

        self.assertEqual(sorted(list(c.keys())), sorted(['foo', 'bar', 'baz']))
        self.assertEqual(sorted(list(c)), sorted(['foo', 'bar', 'baz']))

    def test_register_calls_provider_register(self):
        c = MedleyContainer()
        provider = Mock(register=Mock())

        c.register(provider)
        provider.register.assert_called_with(c)

    def test_register_does_not_call_setitem_when_no_second_argument(self):
        c = MedleyContainer()
        provider = Mock(register=Mock())

        with patch.object(c, '__setitem__') as setitem:
            c.register(provider)
            setitem.assert_not_called()

    def test_register_sets_ids_from_second_argument(self):
        c = MedleyContainer()
        provider = Mock(register=Mock())

        with patch.object(c, '__setitem__') as setitem:
            c.register(provider, {
                'foo': self.foo,
                'bar': self.bar,
                'baz': self.baz
            })

            self.assertEqual(setitem.call_count, 3)

    def test_register_returns_c(self):
        c = MedleyContainer()
        provider = Mock(register=Mock())

        self.assertEqual(c.register(provider), c)

    def test_setitem_throws_error_if_id_frozen(self):
        c = MedleyContainer()
        c._frozen = Mock(__contains__=Mock(return_value=True))

        with self.assertRaises(Exception):
            c.__setitem__('foo', self.foo)

    def test_setitem_adds_id_to_both_values_and_keys_attr(self):
        c = MedleyContainer()
        c._frozen = Mock(__contains__=Mock(return_value=False))
        c._keys = Mock(add=Mock())
        c._values = MagicMock()

        c.__setitem__('foo', self.foo)
        c._values.__setitem__.assert_called_with('foo', self.foo)
        c._keys.add.assert_called_with('foo')

    def test_setitem_allows_non_function_values(self):
        c = MedleyContainer()
        c._frozen = Mock(__contains__=Mock(return_value=False))
        c._keys = Mock(add=Mock())
        c._values = MagicMock()

        c.__setitem__('str', 'str')
        c._keys.add.assert_called_with('str')
        c._values.__setitem__.assert_called_with('str', 'str')

        c.__setitem__('dict', {})
        c._keys.add.assert_called_with('dict')
        c._values.__setitem__.assert_called_with('dict', {})

        c.__setitem__('list', [])
        c._keys.add.assert_called_with('list')
        c._values.__setitem__.assert_called_with('list', [])

        c.__setitem__('tuple', ('foo', 'bar'))
        c._keys.add.assert_called_with('tuple')
        c._values.__setitem__.assert_called_with('tuple', ('foo', 'bar'))

        c.__setitem__('range', range(10))
        c._keys.add.assert_called_with('range')
        c._values.__setitem__.assert_called_with('range', range(10))

        c.__setitem__('regex', r'foo')
        c._keys.add.assert_called_with('regex')
        c._values.__setitem__.assert_called_with('regex', r'foo')

        c.__setitem__('set', set())
        c._keys.add.assert_called_with('set')
        c._values.__setitem__.assert_called_with('set', set())

        c.__setitem__('frozenset', frozenset())
        c._keys.add.assert_called_with('frozenset')
        c._values.__setitem__.assert_called_with('frozenset', frozenset())

        c.__setitem__('boolean', False)
        c._keys.add.assert_called_with('boolean')
        c._values.__setitem__.assert_called_with('boolean', False)

        c.__setitem__('int', int(10))
        c._keys.add.assert_called_with('int')
        c._values.__setitem__.assert_called_with('int', int(10))

        c.__setitem__('float', float(10.1))
        c._keys.add.assert_called_with('float')
        c._values.__setitem__.assert_called_with('float', float(10.1))

        c.__setitem__('complex', complex(10))
        c._keys.add.assert_called_with('complex')
        c._values.__setitem__.assert_called_with('complex', complex(10))

        c.__setitem__('unicode', u'unicode')
        c._keys.add.assert_called_with('unicode')
        c._values.__setitem__.assert_called_with('unicode', u'unicode')

        c.__setitem__('bytes', b'bytes')
        c._keys.add.assert_called_with('bytes')
        c._values.__setitem__.assert_called_with('bytes', b'bytes')

        c.__setitem__('bytearray', bytearray(b'bytearray'))
        c._keys.add.assert_called_with('bytearray')
        c._values.__setitem__.assert_called_with('bytearray', bytearray(b'bytearray'))

        c.__setitem__('none', None)
        c._keys.add.assert_called_with('none')
        c._values.__setitem__.assert_called_with('none', None)

    def test_getitem_throws_error_if_id_does_not_exist(self):
        c = MedleyContainer()
        c._keys = Mock(__contains__=Mock(return_value=False))

        with self.assertRaises(Exception):
            c.__getitem__('foo')

    def test_getitem_returns_raw_function_when_id_in_raw_set(self):
        c = MedleyContainer()
        c._keys = Mock(__contains__=Mock(return_value=True))
        c._protected = Mock(__contains__=Mock(return_value=False))

        c._raw = {'foo': self.foo}
        c._values = {'foo': self.foo}

        self.assertEqual(c.__getitem__('foo'), self.foo)

    def test_getitem_returns_value_when_id_is_not_function(self):
        c = MedleyContainer()
        c._keys = Mock(__contains__=Mock(return_value=True))
        c._protected = Mock(__contains__=Mock(return_value=False))

        c._values = {
            'foo': 'foo',
            'bar': {},
            'baz': [],
            'bat': False
        }

        self.assertEqual(c.__getitem__('foo'), 'foo')
        self.assertEqual(c.__getitem__('bar'), {})
        self.assertEqual(c.__getitem__('baz'), [])
        self.assertEqual(c.__getitem__('bat'), False)

    def test_getitem_returns_raw_function_when_id_in_protected_set(self):
        c = MedleyContainer()
        c._keys = Mock(__contains__=Mock(return_value=True))
        c._protected = Mock(__contains__=Mock(return_value=True))

        c._values = {
            'foo': self.foo
        }

        self.assertEqual(c.__getitem__('foo'), self.foo)

    def test_getitem_executes_factory_if_exists(self):
        c = MedleyContainer()
        c._keys = Mock(__contains__=Mock(return_value=True))
        c._protected = Mock(__contains__=Mock(return_value=False))
        c._factories = Mock(__contains__=Mock(return_value=True))

        c._values = {'foo': self.foo}

        self.assertEqual(c.__getitem__('foo'), 'foo')
        self.foo.assert_called_once_with(c)

    def test_getitem_stores_raw_function_and_freezes(self):
        c = MedleyContainer()
        c._keys = Mock(__contains__=Mock(return_value=True))
        c._protected = Mock(__contains__=Mock(return_value=False))
        c._factories = Mock(__contains__=Mock(return_value=False))
        c._frozen = Mock(add=Mock())

        c._values = {'foo': self.foo}

        self.assertEqual(c.__getitem__('foo'), 'foo')
        self.assertEqual(c._values, {'foo': 'foo'})
        self.assertEqual(c._raw, {'foo': self.foo})
        c._frozen.add.assert_called_with('foo')

    def test_delitem_returns_falsy_when_id_does_not_exist(self):
        c = MedleyContainer()
        c._keys = Mock(__contains__=Mock(return_value=False))

        self.assertFalse(c.__delitem__('foo'))

    def test_delitem_deletes_from_everywhere_wwhen_id_is_function(self):
        c = MedleyContainer()
        c._keys = Mock(__contains__=Mock(return_value=True), discard=Mock())
        c._protected = Mock(discard=Mock())
        c._factories = Mock(discard=Mock())
        c._frozen = Mock(discard=Mock())

        c._values = {'foo': self.foo}
        c._raw = {'foo': self.foo}

        self.assertFalse(c.__delitem__('foo'))
        c._factories.discard.assert_called_with(self.foo)
        c._protected.discard.assert_called_with(self.foo)
        self.assertEqual(c._values, {})
        self.assertEqual(c._raw, {})
        c._frozen.discard.assert_called_with('foo')
        c._keys.discard.assert_called_with('foo')

    def test_delitem_does_not_delete_from_factories_or_protected_when_id_is_str(self):
        c = MedleyContainer()
        c._keys = Mock(__contains__=Mock(return_value=True), discard=Mock())
        c._protected = Mock(discard=Mock())
        c._factories = Mock(discard=Mock())
        c._frozen = Mock(discard=Mock())

        c._values = {'foo': 'foo'}
        c.__delitem__('foo')

        c._factories.discard.assert_not_called()
        c._protected.discard.assert_not_called()
        self.assertEqual(c._values, {})
        self.assertEqual(c._raw, {})
        c._frozen.discard.assert_called_with('foo')
        c._keys.discard.assert_called_with('foo')
