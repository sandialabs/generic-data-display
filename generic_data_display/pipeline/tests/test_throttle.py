import unittest
import queue

from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.preprocessors.throttle import Throttler
from generic_data_display.pipeline.utilities.access_wrapper import AccessWrapper, ConfWrapper


class TestThrottle(unittest.TestCase):
    class TestClass(object):
        def __init__(self):
            self.throttled_field = 0
            self.field_one = 1
            self.field_two = 2

    test_dict = dict(
        throttled_field=0,
        field_one=1,
        field_two=2
    )

    def test_basic_throttle(self):
        log.setLevel("TRACE")
        test_config = {
            "fields": ["throttled_field"],
            "throttle_rate_ms": 100
        }

        throttler = Throttler(None, None, **test_config)
        data = ConfWrapper(self.TestClass())
        self.assertEqual(data['key:throttled_field'], 0)
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)

        # first throttle shouldn't do anything
        throttler.process(data)
        self.assertEqual(data['key:throttled_field'], 0)
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)

        # second throttle should add to throttle list
        throttler.process(data)
        self.assertRaisesRegex(KeyError, "'throttled'", data.__getitem__, 'key:throttled_field')
        self.assertTrue(data.is_throttled("throttled_field"))
        self.assertEqual(set(data.keys()), set(['field_one', 'field_two']))
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)


if __name__ == '__main__':
    unittest.main()
