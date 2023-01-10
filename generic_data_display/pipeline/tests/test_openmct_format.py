import unittest
import datetime
import time

import generic_data_display.pipeline.output_generators.openmct.dictionary_provider as provider
import generic_data_display.pipeline.output_generators.openmct.message_generator as generator
import generic_data_display.pipeline.utilities.access_wrapper as aw
from generic_data_display.pipeline.utilities.type_wrapper import TypeWrapper

from generic_data_display.utilities.logger import log


class TestAccessWrapper(unittest.TestCase):
    time = datetime.datetime.now().timestamp() * 1000

    def setUp(self):
        provider.global_mct_dictionary = {
            "measurements": [
                dict(
                    key=provider.root_folder_key,
                    name="GD2 Data",
                    type="folder",
                    location="ROOT",
                    composition=[]
                )
            ]
        }
        self.test_dict = {
            'field_one': 1,
            'field_two': 2,
            'random_field': 'random',
            'custom_time': self.time,
            'field_three': TypeWrapper(3),
            'nested': {
                'field_four': TypeWrapper(4),
                'stuff': {
                    'field_five': TypeWrapper(5)
                },
            }
        }

    def test_get_item(self):
        self.assertEqual(provider.get_item("bad"), None)
        self.assertEqual(provider.get_item(provider.root_folder_key)['key'], provider.root_folder_key)

    def test_create_folder(self):
        provider.create_folder("test1", "generic_namespace")
        provider.create_folder("test2", "generic_namespace", provider.root_folder_key)
        provider.create_folder("test_sub", "generic_namespace", "test1")
        provider.create_folder("test_bad", "generic_namespace", "bad_folder")

        self.assertEqual(len(provider.global_mct_dictionary['measurements']), 5)
        item = provider.get_item("test1")
        self.assertEqual(item['name'], "test1")
        self.assertEqual(item['key'], "test1")
        self.assertEqual(item['type'], "folder")
        self.assertEqual(item['location'], f"generic_namespace:{provider.root_folder_key}")
        self.assertListEqual(item['composition'], [{"namespace": "generic_namespace", "key": "test_sub"}])

        item = provider.get_item("test2")
        self.assertEqual(item['name'], "test2")
        self.assertEqual(item['key'], "test2")
        self.assertEqual(item['type'], "folder")
        self.assertEqual(item['location'], f"generic_namespace:{provider.root_folder_key}")
        self.assertListEqual(item['composition'], [])

        item = provider.get_item("test_sub")
        self.assertEqual(item['name'], "test_sub")
        self.assertEqual(item['key'], "test_sub")
        self.assertEqual(item['type'], "folder")
        self.assertEqual(item['location'], "generic_namespace:test1")
        self.assertListEqual(item['composition'], [])

        item = provider.get_item("test_bad")
        self.assertEqual(item['name'], "test_bad")
        self.assertEqual(item['key'], "test_bad")
        self.assertEqual(item['type'], "folder")
        self.assertEqual(item['location'], f"generic_namespace:{provider.root_folder_key}")
        self.assertListEqual(item['composition'], [])

        item = provider.get_item(provider.root_folder_key)
        self.assertEqual(item['name'], "GD2 Data")
        self.assertEqual(item['key'], provider.root_folder_key)
        self.assertEqual(item['type'], "folder")
        self.assertEqual(item['location'], "ROOT")
        self.assertListEqual(item['composition'], [{"namespace": "generic_namespace", "key": "test1"},
                                                   {"namespace": "generic_namespace", "key": "test2"},
                                                   {"namespace": "generic_namespace", "key": "test_bad"}])

    def test_create_layout(self):
        config = {
            "config_name": "generic_namespace",
            "data": [
                {
                    "name": "group_one",
                    "type": "layout",
                    "rowsLayout": False,
                    "format": [
                        ["field_one", "field_two"],
                        ["custom_time"]
                    ]
                },
                {
                    "name": "group_bad",
                    "type": "layout",
                    "format": []
                },
                {
                    "name": "group_no_row",
                    "type": "layout",
                    "format": [
                        ['ok'],
                        [],
                        []
                    ]
                }
            ]
        }

        provider.create_layout(config, config['data'][0], provider.root_folder_key)
        provider.create_layout(config, config['data'][1], provider.root_folder_key)
        provider.create_layout(config, config['data'][2], provider.root_folder_key)
        self.assertEqual(len(provider.global_mct_dictionary['measurements']), 4)
        item = provider.get_item("group_one")
        self.assertEqual(item['name'], "group_one")
        self.assertEqual(item['key'], "group_one")
        self.assertEqual(item['type'], "flexible-layout")
        self.assertEqual(item['location'], f"generic_namespace:{provider.root_folder_key}")
        self.assertListEqual(item['composition'],
                             [{"namespace": "generic_namespace", "key": "field_one"}, {"namespace": "generic_namespace", "key": "field_two"},
                              {"namespace": "generic_namespace", "key": "custom_time"}])
        self.assertEqual(item['configuration']['rowsLayout'], False)
        self.assertEqual(item['configuration']['containers'][0]['id'], "container1")
        self.assertEqual(item['configuration']['containers'][0]['size'], 50)
        self.assertDictEqual(item['configuration']['containers'][0]['frames'][0],
                             {"id": "container1-frame1",
                              "domainObjectIdentifier":  {'key': 'field_one', 'namespace': 'generic_namespace'},
                              "size": 50,
                              "noFrame": False})
        self.assertDictEqual(item['configuration']['containers'][0]['frames'][1],
                             {"id": "container1-frame2",
                              "domainObjectIdentifier":  {'key': 'field_two', 'namespace': 'generic_namespace'},
                              "size": 50,
                              "noFrame": False})
        self.assertEqual(item['configuration']['containers'][1]['id'], "container2")
        self.assertEqual(item['configuration']['containers'][1]['size'], 50)
        self.assertDictEqual(item['configuration']['containers'][1]['frames'][0],
                             {"id": "container2-frame1",
                              "domainObjectIdentifier": {'key': 'custom_time', 'namespace': 'generic_namespace'},
                              "size": 100,
                              "noFrame": False})
        item = provider.get_item("group_bad")
        self.assertEqual(item['name'], "group_bad")
        self.assertEqual(item['key'], "group_bad")
        self.assertEqual(item['type'], "flexible-layout")
        self.assertEqual(item['location'], f"generic_namespace:{provider.root_folder_key}")
        self.assertListEqual(item['composition'], [])
        self.assertEqual(item['configuration']['rowsLayout'], True)
        self.assertEqual(item['configuration']['containers'], [])

        item = provider.get_item("group_no_row")
        self.assertEqual(item['name'], "group_no_row")
        self.assertEqual(item['key'], "group_no_row")
        self.assertEqual(item['type'], "flexible-layout")
        self.assertEqual(item['location'], f"generic_namespace:{provider.root_folder_key}")
        self.assertListEqual(item['composition'], [{"namespace": "generic_namespace", "key": "ok"}])
        self.assertEqual(item['configuration']['rowsLayout'], True)
        self.assertEqual(item['configuration']['containers'][0]['id'], 'container1')
        self.assertEqual(item['configuration']['containers'][0]['size'], 33)
        self.assertDictEqual(item['configuration']['containers'][0]['frames'][0],
                             {"id": "container1-frame1",
                              "domainObjectIdentifier": {'key': 'ok', 'namespace': 'generic_namespace'},
                              "size": 100,
                              "noFrame": False})
        self.assertEqual(item['configuration']['containers'][1]['id'], 'container2')
        self.assertEqual(item['configuration']['containers'][1]['size'], 33)
        self.assertEqual(item['configuration']['containers'][1]['frames'], [])
        self.assertEqual(item['configuration']['containers'][2]['id'], 'container3')
        self.assertEqual(item['configuration']['containers'][2]['size'], 33)
        self.assertEqual(item['configuration']['containers'][2]['frames'], [])


    def test_add_object(self):
        log.setLevel("TRACE")
        data_config = {
            "name": "field_one"
        }
        wrapper = aw.AccessWrapper(self.test_dict)
        provider.add_object(data_config, wrapper, "field_one", None, 'generic_namespace')
        self.assertEqual(len(provider.global_mct_dictionary['measurements']), 2)
        item = provider.get_item("field_one")
        self.assertEqual(item['name'], "field_one")
        self.assertEqual(item['key'], "field_one")
        self.assertEqual(item['type'], "plot.data")
        self.assertEqual(item['telemetry']['values'][0]['name'], "field_one")
        self.assertEqual(item['telemetry']['values'][1]['name'], "Timestamp")
        self.assertEqual(item['location'], f"generic_namespace:{provider.root_folder_key}")
        self.assertEqual(item['namespace'], "generic_namespace")

        # duplicate object, should immediately return
        provider.add_object(data_config, wrapper, "field_one", None, 'generic_namespace')
        self.assertEqual(len(provider.global_mct_dictionary['measurements']), 2)

        # test splitting the data and adding a split object
        wrapper.split("field_one", ":id_0")
        data_config['name'] = data_config['name'] + ':id_0'
        provider.add_object(data_config, wrapper, "field_one:id_0", None, 'generic_namespace')
        item = provider.get_item("field_one:id_0")
        self.assertEqual(len(provider.global_mct_dictionary['measurements']), 3)
        self.assertEqual(item['name'], "field_one:id_0")
        self.assertEqual(item['key'], "field_one:id_0")
        self.assertEqual(item['type'], "plot.data")
        self.assertEqual(item['telemetry']['values'][0]['name'], "field_one:id_0")
        self.assertEqual(item['location'], f"generic_namespace:{provider.root_folder_key}")
        self.assertEqual(item['namespace'], "generic_namespace")

        # duplicate object, should immediately return
        provider.add_object(data_config, wrapper, "field_one:id_0", None, 'generic_namespace')
        self.assertEqual(len(provider.global_mct_dictionary['measurements']), 3)

    def test_generate_messages(self):
        config = {
            "data": [
                {
                    "name": "field_one",
                },
                {
                    "name": "field_two",
                    "domain_key": "custom_time"
                }
            ]
        }
        data_object = aw.ConfWrapper(self.test_dict)
        messages = generator.generate_messages(config, data_object)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['topic'], "field_one")
        self.assertGreater(messages[0]['utc'], self.time)
        self.assertEqual(messages[0]['field_one'], 1)
        self.assertEqual(messages[1]['topic'], "field_two")
        self.assertEqual(messages[1]['custom_time'], self.time)
        self.assertEqual(messages[1]['field_two'], 2)

        self.assertEqual(len(provider.global_mct_dictionary['measurements']), 3)
        item = provider.get_item("field_one")
        self.assertEqual(item['name'], "field_one")
        self.assertEqual(item['key'], "field_one")
        self.assertEqual(item['type'], "plot.data")
        self.assertEqual(item['telemetry']['values'][0]['name'], "field_one")
        self.assertEqual(item['telemetry']['values'][1]['name'], "Timestamp")
        self.assertEqual(item['location'], f"root-object:{provider.root_folder_key}")

        # test splitting and adding a new folder name
        data_object.split("field_one", ":id_5")
        config['config_name'] = "config_folder"
        provider.create_folder("config_folder", "generic_namespace")
        messages = generator.generate_messages(config, data_object)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['topic'], "field_one:id_5")
        self.assertGreater(messages[0]['utc'], self.time)
        self.assertEqual(messages[0]['field_one:id_5'], 1)

        self.assertEqual(len(provider.global_mct_dictionary['measurements']), 5)
        item = provider.get_item("field_one:id_5")
        self.assertEqual(item['name'], "field_one:id_5")
        self.assertEqual(item['key'], "field_one:id_5")
        self.assertEqual(item['type'], "plot.data")
        self.assertEqual(item['telemetry']['values'][0]['name'], "field_one:id_5")
        self.assertEqual(item['telemetry']['values'][1]['name'], "Timestamp")
        self.assertEqual(item['location'], "config_folder:config_folder")

    def test_sanitize(self):
        config = {
            "data": [
                {
                    "name": "field/zero",
                },
            ]
        }
        test_dict = {"field": {"zero": 0}}

        data_object = aw.ConfWrapper(test_dict)
        messages = generator.generate_messages(config, data_object)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['topic'], 'field.zero')
        self.assertEqual(messages[0]['field.zero'], 0)

    def test_pass_all_omct(self):
        config = {
            'data': [
                {
                    'name': 'field_one',
                },
                {
                    'name': 'field_two',
                    'domain_key': 'custom_time'
                }
            ],
            'pass_all_omct': True,
            'pass_bfs_depth': 1,
        }
        data_object = aw.ConfWrapper(self.test_dict)
        messages = generator.generate_messages(config, data_object)
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]['topic'], 'field_one')
        self.assertEqual(messages[1]['topic'], 'field_two')
        self.assertEqual(messages[2]['topic'], 'field_three')
        self.assertEqual(messages[2]['field_three'], 3)

        config['pass_bfs_depth'] = 2
        messages = generator.generate_messages(config, data_object)
        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0]['topic'], 'field_one')
        self.assertEqual(messages[1]['topic'], 'field_two')
        self.assertEqual(messages[2]['topic'], 'field_three')
        self.assertEqual(messages[2]['field_three'], 3)
        self.assertEqual(messages[3]['topic'], 'nested.field_four')
        self.assertEqual(messages[3]['nested.field_four'], 4)

        del config['pass_bfs_depth']
        messages = generator.generate_messages(config, data_object)
        self.assertEqual(len(messages), 5)
        self.assertEqual(messages[0]['topic'], 'field_one')
        self.assertEqual(messages[1]['topic'], 'field_two')
        self.assertEqual(messages[2]['topic'], 'field_three')
        self.assertEqual(messages[2]['field_three'], 3)
        self.assertEqual(messages[3]['topic'], 'nested.field_four')
        self.assertEqual(messages[3]['nested.field_four'], 4)
        self.assertEqual(messages[4]['topic'], 'nested.stuff.field_five')
        self.assertEqual(messages[4]['nested.stuff.field_five'], 5)

        del config['pass_all_omct']
        messages = generator.generate_messages(config, data_object)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['topic'], 'field_one')
        self.assertEqual(messages[1]['topic'], 'field_two')

    def test_timeout(self):
        config = {
            "data": [
                {
                    "name": "field_one",
                }
            ],
            "data_timeout_sec": 1
        }
        data_object = aw.ConfWrapper(self.test_dict)
        messages = generator.generate_messages(config, data_object)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['topic'], "field_one")
        self.assertGreater(messages[0]['utc'], self.time)
        self.assertEqual(messages[0]['field_one'], 1)

        self.assertEqual(len(provider.global_mct_dictionary['measurements']), 2)
        item = provider.get_item("field_one")
        self.assertEqual(item['name'], "field_one")
        self.assertEqual(item['key'], "field_one")
        self.assertEqual(item['type'], "plot.data")
        self.assertEqual(item['telemetry']['values'][0]['name'], "field_one")
        self.assertEqual(item['telemetry']['values'][1]['name'], "Timestamp")
        self.assertEqual(item['location'], f"root-object:{provider.root_folder_key}")

        time.sleep(2)

        self.test_dict2 = {'field_two': 17}
        data_object = aw.ConfWrapper(self.test_dict2)
        messages = generator.generate_messages(config, data_object)
        self.assertEqual(len(messages), 0)

        self.assertEqual(len(provider.global_mct_dictionary['measurements']), 1)
        self.assertIsNone(provider.get_item("field_one"))


if __name__ == '__main__':
    unittest.main()
