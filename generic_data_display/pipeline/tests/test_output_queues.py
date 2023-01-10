import unittest
import queue

from generic_data_display.pipeline.utilities.output_queues import OutputQueues


class TestOutputQueues(unittest.TestCase):
    def test_operators(self):
        queues = OutputQueues()
        self.assertFalse(bool(queues))
        self.assertRaises(KeyError, lambda: queues['key'])

        queues.add_key('key')
        self.assertTrue(bool(queues))
        self.assertEqual([], queues['key'])

        push_queue = queues.get_queue('key')
        self.assertEqual(1, len(queues['key']))
        self.assertEqual(push_queue, queues['key'][0])

        push_queue_2 = queues.get_queue('new_key')
        self.assertEqual(1, len(queues['new_key']))
        self.assertEqual(push_queue_2, queues['new_key'][0])

        push_queue_3 = queues.get_queue('new_key')
        self.assertEqual(2, len(queues['new_key']))
        self.assertEqual(push_queue_2, queues['new_key'][0])
        self.assertEqual(push_queue_3, queues['new_key'][1])

    def test_merge(self):
        queues_1 = OutputQueues()
        queues_1.get_queue('key_1')
        queues_1.get_queue('key_1')
        queues_1.get_queue('key_2')

        queues_2 = OutputQueues()
        queues_2.get_queue('key_3')
        queues_2.get_queue('key_1')

        queues_3 = {'key_1': [], 'key_4': []}
        queues_3['key_1'].append(queue.Queue())
        queues_3['key_1'].append(queue.Queue())
        queues_3['key_4'].append(queue.Queue())

        queues_merge = OutputQueues()
        queues_merge.merge(queues_1)
        queues_merge.merge(queues_2)
        queues_merge.merge(queues_3)

        self.assertEqual(5, len(queues_merge['key_1']))
        self.assertEqual(1, len(queues_merge['key_2']))
        self.assertEqual(1, len(queues_merge['key_3']))
        self.assertEqual(1, len(queues_merge['key_4']))


if __name__ == '__main__':
    unittest.main()
