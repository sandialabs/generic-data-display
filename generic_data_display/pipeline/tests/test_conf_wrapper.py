import unittest
from generic_data_display.pipeline.utilities.access_wrapper import AccessWrapper, ConfWrapper, _flatten


class TestConfWrapper(unittest.TestCase):
    class TestClass(object):
        x = 1
        y = 'y'

        def __init__(self):
            self.k = 'value'

    test_config = {
        "trivial": "key:x",
        "raster": "match:stream[0-9]+/raster",
        "info": "sub:#1/meta",
        "things": ["one", "key:y", "hmmm"],
        "dict": {
            "more": "stuff"
        }
    }

    test_dict = {
        'x': 1,
        'y': 'y',
        'k': 'value',
        'stream0': {
            'raster': 10,
            'meta': 'oh no!'
        },
        'stream11': {
            'raster': 20,
            'meta': 'woah!'
        },
        'dummy_nested_array': [
            {'value': 13}
        ],
        'nested_array': [
            {'value': 13},
            {'value': 14},
            {'value': 15},
            {'value': 16}
        ]
    }

    def test_attr_access(self):
        tester = ConfWrapper(self.TestClass())
        self.assertEqual(tester['key:x'], 1)
        self.assertEqual(tester['key:y'], 'y')
        self.assertEqual(tester['key:k'], 'value')
        self.assertRaises(TypeError, tester.__getitem__, 'key:bad_field')

    def test_dict_access(self):
        tester = ConfWrapper(self.test_dict)
        self.assertEqual(tester['key:x'], 1)
        self.assertEqual(tester['key:y'], 'y')
        self.assertEqual(tester['key:k'], 'value')
        self.assertRaises(KeyError, tester.__getitem__, 'key:bad_field')

    def test_array_access(self):
        tester = ConfWrapper(self.test_dict)
        self.assertEqual(tester['key:nested_array/0/value'], 13)

    def test_array_match_count(self):
        data_obj = AccessWrapper(self.test_dict)
        matches = list(ConfWrapper.MatchAll({"array": "match:nested_array/([0-9]+)/value"}, data_obj))
        self.assertEqual(len(matches), 4)

    def test_array_match_and_sub(self):
        data_obj = AccessWrapper(self.test_dict)
        matches = list(ConfWrapper.MatchAll({"array": "match:dummy_nested_array/([0-9]+)/value"}, data_obj))
        self.assertEqual(len(matches), 1)
        sub = matches[0]['sub:dummy_nested_array/#0/value']
        self.assertEqual(sub, 13)
        self.assertEqual(matches[0].get_match(), "dummy_nested_array/0/value")

    def test_add_item(self):
        tester = ConfWrapper(self.test_dict)
        tester['pow'] = 'pow'
        self.assertEqual(tester['key:pow'], 'pow')
        tester['x'] = 2
        self.assertEqual(tester['key:x'], 2)
        tester['key:thing'] = 32
        self.assertEqual(tester['key:thing'], 32)

    def test_flatten(self):
        flat = _flatten(self.test_config)
        self.assertEqual(flat, {"key:x", "match:stream[0-9]+/raster", "sub:#1/meta", "one", "key:y", "hmmm", "stuff"})

    def test_match_all(self):
        data_obj = AccessWrapper(self.test_dict)
        matches = list(ConfWrapper.MatchAll(self.test_config, data_obj))
        self.assertEqual(len(matches), 2)


if __name__ == '__main__':
    unittest.main()
