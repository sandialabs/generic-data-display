import unittest
import queue

from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.utilities.tee_queue import TeeQueue
from generic_data_display.pipeline.utilities.access_wrapper import AccessWrapper


class TestOutputQueues(unittest.TestCase):
    def setUp(self):
        self.pop_queue = queue.Queue()
        self.tee_queue = TeeQueue(self.pop_queue)

    def tearDown(self):
        self.tee_queue.join()

    def test_run(self):
        log.setLevel('TRACE')

        self.assertFalse(bool(self.tee_queue))
        push_queue_1 = self.tee_queue.get_queue()
        push_queue_2 = self.tee_queue.get_queue()

        self.assertTrue(bool(self.tee_queue))
        self.tee_queue.start()

        data = {'key_1': 1, 'key_2': [1, 2, 3]}
        data_object = AccessWrapper(data)
        self.pop_queue.put(data_object)

        object_1 = push_queue_1.get(block=True, timeout=1)
        object_2 = push_queue_2.get(block=True, timeout=1)

        # Check Equality of objects
        # We want object_1 = object_2 since they reference the same object
        # a deep_copy of a data_object could be potentially expensive
        # for now just document that tee queue duplicates are reference copies
        self.assertEqual(data_object, object_1)
        self.assertEqual(data_object, object_2)
        object_1['new'] = 'new'
        self.assertEqual(object_1, object_2)


if __name__ == '__main__':
    unittest.main()

