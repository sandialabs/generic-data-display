import copy
import datetime
import queue
import unittest

from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.preprocessors.split_by_key import SplitByKey
from generic_data_display.pipeline.output_generators.openmct_generator import OpenMctGenerator
from generic_data_display.pipeline.utilities.access_wrapper import ConfWrapper


class TestSplitByKey(unittest.TestCase):
    class TestClass(object):
        def __init__(self):
            self.key_field = 0
            self.key_field_extra = 14
            self.field_one = 1
            self.field_two = 2

    test_dict = dict(
        key_field=0,
        key_field_extra=14,
        field_one=1,
        field_two=2
    )

    test_app_config = {
        "description": "Test",
        "version": "1.0",
        "config": [
            {
                "name": "test_config",
                "output": [
                    {
                        "name": "openmct_display",
                        "config": {
                            "data": [
                                {
                                    "name": "field_one",
                                },
                                {
                                    "name": "added_field"
                                },
                                {
                                    "name": "recursive_field"
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "name": "extra_config",
                "output": [
                    {
                        "name": "openmct_display",
                        "config": {
                            "data": [
                                {
                                    "name": "field_bad"
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    def test_value_split_class(self):
        log.setLevel("TRACE")
        test_config = {
            "key_fields": {"key:key_field": [0, 1, 2]},
            "value_fields": ["field_one", "field_two", "key_field", "added_field"],
            "clear_dict_ms": 60000
        }

        split_by_key = SplitByKey(None, None, config_name="test_config", **test_config)
        data = ConfWrapper(self.TestClass())
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)
        self.assertEqual(data['key:key_field'], 0)
        self.assertFalse(data.is_split)

        split_by_key.process(data)
        self.assertEqual(data['key:field_one:0'], 1)
        self.assertEqual(data['key:field_two:0'], 2)
        self.assertEqual(data['key:key_field:0'], 0)
        self.assertTrue(data.is_split)

        # the fields values were updated in a prior run, should do nothing
        split_by_key.process(data)
        self.assertEqual(data['key:field_one:0'], 1)
        self.assertEqual(data['key:field_two:0'], 2)
        self.assertEqual(data['key:key_field:0'], 0)

        # Adding a new field that matches a name in the value_fields list
        data['added_field'] = 5
        self.assertEqual(data['key:added_field:0'], 5)

        # Adding a new field that does not match a name in the value_fields list
        data['funky_field'] = "so funky"
        self.assertEqual(data['key:funky_field'], "so funky")

        # Getting a field that was in the value fields list
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)
        self.assertEqual(data['key:key_field'], 0)
        self.assertEqual(data['key:added_field'], 5)

    def test_value_split_dict(self):
        log.setLevel("TRACE")
        test_dict = copy.deepcopy(self.test_dict)
        test_config = {
            "key_fields": {"key:key_field": []},
            "value_fields": ["field_one", "field_two", "key_field", "added_field"],
            "clear_dict_ms": 60000
        }

        split_by_key = SplitByKey(None, None, config_name="test_config", **test_config)
        data = ConfWrapper(test_dict)
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)
        self.assertEqual(data['key:key_field'], 0)
        self.assertFalse(data.is_split)

        split_by_key.process(data)
        self.assertEqual(data['key:field_one:0'], 1)
        self.assertEqual(data['key:field_two:0'], 2)
        self.assertEqual(data['key:key_field:0'], 0)
        self.assertTrue(data.is_split)

        # the fields values were updated in a prior run, should do nothing
        split_by_key.process(data)
        self.assertEqual(data['key:field_one:0'], 1)
        self.assertEqual(data['key:field_two:0'], 2)
        self.assertEqual(data['key:key_field:0'], 0)

        # Adding a new field that matches a name in the value_fields list
        data['added_field'] = 5
        self.assertEqual(data['key:added_field:0'], 5)

        # Adding a new field that does not match a name in the value_fields list
        data['funky_field'] = "so funky"
        self.assertEqual(data['key:funky_field'], "so funky")

        # Getting a field that was in the value fields list
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)
        self.assertEqual(data['key:key_field'], 0)
        self.assertEqual(data['key:added_field'], 5)

    def test_recursive_split_class(self):
        log.setLevel("TRACE")
        test_config = {
            "key_fields": {"key:key_field": []},
            "clear_dict_ms": 60000
        }

        split_by_key = SplitByKey(None, None, config_name="test_config", **test_config)
        data = ConfWrapper(self.TestClass())
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)
        self.assertEqual(data['key:key_field'], 0)
        self.assertFalse(data.is_split)

        split_by_key.process(data)
        self.assertEqual(data['key:field_one:0'], 1)
        self.assertEqual(data['key:field_two:0'], 2)
        self.assertEqual(data['key:key_field:0'], 0)
        self.assertTrue(data.is_split)

        # the fields values were updated in a prior run, should do nothing
        split_by_key.process(data)
        self.assertEqual(data['key:field_one:0'], 1)
        self.assertEqual(data['key:field_two:0'], 2)
        self.assertEqual(data['key:key_field:0'], 0)

        # Adding a new field should auto populate key
        data['added_field'] = 5
        self.assertEqual(data['key:added_field:0'], 5)

        # Getting a field that was in the value fields list
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)
        self.assertEqual(data['key:key_field'], 0)
        self.assertEqual(data['key:added_field'], 5)

    def test_recursive_split_dict(self):
        log.setLevel("TRACE")
        test_dict = copy.deepcopy(self.test_dict)
        test_config = {
            "key_fields": {"key:key_field": [0, 1, 2]},
            "clear_dict_ms": 60000
        }

        split_by_key = SplitByKey(None, None, config_name="test_config", **test_config)
        data = ConfWrapper(test_dict)
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)
        self.assertEqual(data['key:key_field'], 0)
        self.assertFalse(data.is_split)

        split_by_key.process(data)
        self.assertEqual(data['key:field_one:0'], 1)
        self.assertEqual(data['key:field_two:0'], 2)
        self.assertEqual(data['key:key_field:0'], 0)
        self.assertTrue(data.is_split)

        # the fields values were updated in a prior run, should do nothing
        split_by_key.process(data)
        self.assertEqual(data['key:field_one:0'], 1)
        self.assertEqual(data['key:field_two:0'], 2)
        self.assertEqual(data['key:key_field:0'], 0)

        # Adding a new field should auto populate key
        data['added_field'] = 5
        self.assertEqual(data['key:added_field:0'], 5)

        # Getting a field that was in the value fields list
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)
        self.assertEqual(data['key:key_field'], 0)
        self.assertEqual(data['key:added_field'], 5)

    def test_multi_key_value_split(self):
        log.setLevel("TRACE")
        test_dict = copy.deepcopy(self.test_dict)
        test_config = {
            "key_fields": {"key:key_field": [0, 1, 2], "key:key_field_extra": []},
            "value_fields": ["field_one", "field_two", "added_field"],
            "clear_dict_ms": 60000
        }

        split_by_key = SplitByKey(None, None, config_name="test_config", **test_config)
        data = ConfWrapper(test_dict)
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)
        self.assertFalse(data.is_split)

        split_by_key.process(data)
        self.assertEqual(data['key:field_one:0:14'], 1)
        self.assertEqual(data['key:field_two:0:14'], 2)
        self.assertTrue(data.is_split)

        # the fields values were updated in a prior run, should do nothing
        split_by_key.process(data)
        self.assertEqual(data['key:field_one:0:14'], 1)
        self.assertEqual(data['key:field_two:0:14'], 2)

        # Adding a new field should auto populate key
        data['added_field'] = 5
        self.assertEqual(data['key:added_field:0:14'], 5)

        # Getting a field that was in the value fields list
        self.assertEqual(data['key:field_one'], 1)
        self.assertEqual(data['key:field_two'], 2)
        self.assertEqual(data['key:added_field'], 5)

    def test_split_by_key_and_message_converter(self):
        log.setLevel("TRACE")
        test_config = {
            "key_fields": {"key:key_field": [0, 1, 2]},
            "value_fields": ["field_one", "field_two", "added_field"],
            "clear_dict_ms": 60000
        }

        output_queue = queue.Queue()
        test_dict = copy.deepcopy(self.test_dict)
        split_by_key = SplitByKey(None, None, config_name="test_config", **test_config)
        message_converter = OpenMctGenerator(None,
                                            output_queue,
                                            config_name="test_config",
                                            root_config=self.test_app_config['config'][0]['output'],
                                            data=self.test_app_config['config'][0]['output'][0]['config']['data'],
                                            local_testing=True)
        data = ConfWrapper(test_dict)

        split_by_key.process(data)

        message_converter.process(data)
        try:
            first_item = output_queue.get(block=False, timeout=None)
            self.assertEqual(first_item['topic'], "field_one:0")
            self.assertLessEqual(first_item['utc'], datetime.datetime.now().timestamp() * 1000)
            self.assertEqual(first_item['field_one:0'], 1)
        except queue.Empty:
            self.assertFalse(True)

        self.assertTrue(output_queue.empty())


if __name__ == '__main__':
    unittest.main()
