import json
from modulefinder import Module
import os
import unittest
import generic_data_display

from generic_data_display.utilities.config import load_file, loads, _create_validator
from generic_data_display.utilities.modules_enum import ModulesEnum
from jsonschema.exceptions import ValidationError


class TestValidation(unittest.TestCase):
    def test_existing_gd2_config_schemas(self):
        error_count = 0
        error_list = []
        schemas = []
        for root, dir, files in os.walk("generic_data_display/data_sim/resources/pipeline_configs"):
            for file in files:
                if file.endswith('.jsonschema') or file.endswith('.json'):
                    schemas.append(root + os.sep + file)

        for schema in schemas:
            try:
                load_file(schema)
            except:
                error_count += 1
                error_list.append(schema)

        if error_count > 0:
            self.fail(error_list)
        else:
            assert len(error_list) == 0

    def test_big_config(self):
        load_file("generic_data_display/pipeline/tests/test_configs/test_config_large.json")

    def test_regex_keys(self):
        # Test that loads() reads in a string or dict and that the key fields for split_by_key validiate
        json_string = """{
            "description": "Example Config For Validating the GD2 JSON Validation",
            "version": "1.0",
            "config": [
                {
                    "name": "tcp_basic",
                    "connection": {
                        "type": "tcp",
                        "method": "connect",
                        "address": "localhost",
                        "port": 21772,
                        "reconnect_attempts": 5,
                        "reconnect_interval_sec": 2
                    },
                    "data": {
                        "format": "kaitai",
                        "kaitai_file": "generic_data_display/data_sim/resources/data_definitions/kaitai/basic_kaitai.ksy"
                    },
                    "preprocessing": [
                        {
                            "name": "split_by_key",
                            "config": {
                                "key_fields": {
                                    "key:metadata/image_subset_id": [
                                        "id_0",
                                        "id_1",
                                        "id_2"
                                    ]
                                },
                                "value_fields": [
                                    "metadata/temperature",
                                    "url0"
                                ],
                                "clear_dict_ms": 60000,
                                "key_delimiter": ":"
                            }
                        }
                    ],
                   "generator": [
                        {
                            "name": "openmct",
                            "id": "openmct",
                            "config": {
                                "data": [
                                {
                                    "name": "image",
                                    "range_key": "url"
                                },
                                {
                                    "name": "image_id"
                                },
                                {
                                    "name": "image_size",
                                    "range_key": "byte_size"
                                },
                                {
                                    "name": "row"
                                }
                                ]
                            }
                        }
                    ],
                    "output" : [
                        {
                            "name": "openmct_display",
                            "consumes": "openmct"
                        }
                    ]
                }
            ]
        }"""
        loads(json_string)

        json_dict = {
            "description": "Example Config For Validating the GD2 JSON Validation",
            "version": "1.0",
            "config": [
                {
                    "name": "tcp_basic",
                    "connection": {
                        "type": "tcp",
                        "method": "connect",
                        "address": "localhost",
                        "port": 21772,
                        "reconnect_attempts": 5,
                        "reconnect_interval_sec": 2
                    },
                    "data": {
                        "format": "kaitai",
                        "kaitai_file": "generic_data_display/data_sim/resources/data_definitions/kaitai/basic_kaitai.ksy"
                    },
                    "preprocessing": [
                        {
                            "name": "split_by_key",
                            "config": {
                                "key_fields": {
                                    "key:metadata/image_subset_id": [
                                        "id_0",
                                        "id_1",
                                        "id_2"
                                    ]
                                },
                                "value_fields": [
                                    "metadata/temperature",
                                    "url0"
                                ],
                                "clear_dict_ms": 60000,
                                "key_delimiter": ":"
                            }
                        }
                    ],
                   "generator": [
                        {
                            "name": "openmct",
                            "id": "openmct",
                            "config": {
                                "data": [
                                {
                                    "name": "image",
                                    "range_key": "url"
                                },
                                {
                                    "name": "image_id"
                                },
                                {
                                    "name": "image_size",
                                    "range_key": "byte_size"
                                },
                                {
                                    "name": "row"
                                }
                                ]
                            }
                        }
                    ],
                    "output" : [
                        {
                            "name": "openmct_display",
                            "consumes": "openmct"
                        }
                    ]
                }
            ]
        }
        loads(json_dict)

        # Test that an invaild key for split_by_key fails
        self.assertRaises(ValidationError, load_file, 'generic_data_display/pipeline/tests/test_configs/test_config_key_fail.json')

    def test_regex_values(self):
        # TODO: Once we're using regex values for values this test needs filled out
        pass

    def test_check_expected_failures(self):
        baseline_json_dict = {
            "description": 1,
            "version": 1,
            "config": [
            {
                "name": 1,
                "connection": {
                    "type": "tcp",
                    "method": "disconnect",
                    "address": 1,
                    "port": "51772"
                },
                "data": {
                    "format": "protobuf",
                    "protobuf_file": 1,
                    "protobuf_class": 1,
                    "prefix_message_size_bytes": "4"
                },
                "preprocessing": [
                    {
                        "name": "throttle",
                        "config": {
                            "fields": [1],
                            "throttle_rate_ms": "100"
                        }
                    },
                    {
                        "name": "base64",
                        "config": {
                            "input": 1,
                            "output": 1,
                            "operation": "recode"
                        }
                    },
                    {
                        "name": "imagify",
                        "config": {
                            "input_array": 1,
                            "datauri": 1,
                            "rows": 1,
                            "cols": 1,
                            "log_level": 1,
                            "input_format": "BGR",
                            "datauri_format": "PMB"
                        }
                    },
                    {
                        "name": "split_by_key",
                        "config": {
                            "key_fields": {
                                "y:/!!!": [
                                    0,
                                    "id_1",
                                    "id_2"
                                ]
                            },
                            "value_fields": [
                                "metadata/temperature",
                                "metadata/voltage",
                                "metadata/nominal_value",
                                0,
                                "url1",
                                "url2",
                                "url3",
                                "url4",
                                "url5",
                                "url6",
                                "url7",
                                "url8",
                                "url9"
                            ],
                            "clear_dict_ms": "60000",
                            "key_delimiter": 1
                        }
                    },
                    {
                        "name": "match",
                        "config": {
                            "matches": [
                                {
                                    "value": 1,
                                    "key": 1
                                }
                            ]
                        }
                    },
                    {
                        "name": "omct_hints",
                        "config": {
                            "confs": [
                                {
                                    "match": "key:row",
                                    "hints": {
                                        "unit": 1,
                                        "format": 1,
                                        "name": 1,
                                        "type": 1
                                    }
                                },
                                {
                                    "match":1
                                }
                            ]
                        }
                    }
                ],
                "generator": [
                    {
                    "name": "openmct",
                    "id": "openmct",
                    "config": {
                        "data": [
                        {
                            "name": "id_1",
                            "type": "layout",
                            "format": [
                            [1],
                            ["temperature:id_1"],
                            ["voltage:id_1"]
                            ]
                        },
                        {
                            "name": "url0",
                            "type": ""
                        },
                        {
                            "name": "temperature",
                            "range_key": "metadata/temperature",
                            "units": "deg C",
                            "type": "potato.data"
                        },
                        {
                            "name": "voltage",
                            "range_key": "metadata/voltage"
                        },
                        {
                            "name": "id_0",
                            "type": "layout",
                            "rowsLayout": "maybe",
                            "format": [
                            ["url0:id_0"],
                            ["temperature:id_0"],
                            ["voltage:id_0", "id_1"]
                            ]
                        }
                        ]
                    }
                    }
                ],
                "output" : [
                    {
                        "name": "openmct_display",
                        "consumes": "openmct"
                    },
                    {
                        "name": "data_store",
                        "consumes": "openmct",
                        "config": {
                            "data_store_host": "127.0.0.1",
                            "data_store_port": 5050
                        }
                    }
                ]
                }
            ]
        }

        validation_error_count = 0
        test_validator = _create_validator(ModulesEnum.PIPELINE)
        validation_errors = test_validator.iter_errors(json.loads(json.dumps(baseline_json_dict)))
        for error in validation_errors:
            validation_error_count += 1
        self.assertEqual(validation_error_count, 12)

if __name__ == '__main__':
    unittest.main()
