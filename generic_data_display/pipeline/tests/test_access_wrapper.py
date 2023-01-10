import unittest
from generic_data_display.pipeline.utilities.access_wrapper import AccessWrapper


class TestAccessWrapper(unittest.TestCase):
    class TestClass(object):
        x = 1
        y = 'y'

        def __init__(self):
            self.k = 'value'

    test_dict = {'x': 1, 'y': 'y', 'k': 'value'}
    test_list = [{'val': 1}, {'val': 2}]

    def test_list_access(self):
        tester = AccessWrapper(self.test_list)
        self.assertEqual(tester['0']['val'], 1)
        self.assertCountEqual(tester.keys(), ['0', '1'])
        self.assertCountEqual([x for x in tester._bfs()], ['0', '1', '0/val', '1/val'])

    def test_timer_functions(self):
        tester = AccessWrapper(self.test_dict)
        tester.timer.start_timing('test')
        tester.timer.start_timing('test')
        tester.timer.stop_timing('whoops')
        tester.timer.stop_timing('test')
        tester.timer.stop_timing('test')
        self.assertEqual(len(tester.timer.keys()), 1)
        self.assertTrue('test' in tester.timer.keys())
        self.assertFalse('whoops' in tester.timer.keys())
        self.assertGreater(tester.timer['test'], 0)
        self.assertEqual(tester.timer.log_string.count('\n'), 4)

    def test_timer_context(self):
        tester = AccessWrapper(self.test_dict)
        with tester.timer('test'):
            tester.timer.start_timing('test')
            tester.timer.stop_timing('whoops')
            tester.timer.stop_timing('test')

        self.assertEqual(len(tester.timer.keys()), 1)
        self.assertTrue('test' in tester.timer.keys())
        self.assertFalse('whoops' in tester.timer.keys())
        self.assertGreater(tester.timer['test'], 0)
        self.assertEqual(tester.timer.log_string.count('\n'), 4)

    def test_throttle(self):
        tester = AccessWrapper(self.test_dict)
        self.assertFalse(tester.is_throttled('x'))
        tester.throttle('x')
        self.assertTrue(tester.is_throttled('x'))
        self.assertFalse(tester.is_throttled('y'))
        self.assertFalse(tester.is_throttled('bad_field'))

    def test_split(self):
        tester = AccessWrapper(self.test_dict)
        self.assertFalse(tester.is_split)
        tester.split('x', ':id_0')
        self.assertTrue(tester.is_split)
        self.assertEqual(tester._key_aliases['x:id_0'], 'x')
        self.assertEqual(tester['x'], 1)
        self.assertEqual(tester['x:id_0'], 1)
        self.assertEqual(tester.get_suffix('x'), ':id_0')
        self.assertEqual(tester.get_suffix('y'), '')

        # Don't support multiple splits on a single data field
        tester.split('x', ':id_1')
        self.assertTrue(tester.is_split)
        self.assertEqual(tester._key_aliases['x:id_0'], 'x')
        self.assertEqual(tester['x'], 1)
        self.assertEqual(tester['x:id_0'], 1)
        self.assertEqual(tester.get_suffix('x'), ':id_0')
        self.assertEqual(tester.get_suffix('y'), '')


if __name__ == '__main__':
    unittest.main()
