import unittest

from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.preprocessors.find_index_by_key import FindIndexByKey
from generic_data_display.pipeline.utilities.access_wrapper import ConfWrapper, AccessWrapper


class TestMatch(unittest.TestCase):
    def test_match(self):
        log.setLevel("TRACE")
        data = {
            'x': 1,
            'y': 2,
            'list': [
                {
                    'name': 'one name',
                    'value': 'awesome',
                    'data': [
                        {'name': 'sub_one', 'value': 'one'},
                        {'name': 'sub_two', 'value': 'two'}
                    ]
                },
                {
                    'name': 'two name',
                    'value': 'fun',
                    'data': [
                        {'name': 'sub_one', 'value': 'one'},
                        {'name': 'sub_two', 'value': 'two'}
                    ]
                },
                {
                    'name': 'x',
                    'value': 'x_value'
                }
            ]
        }
        test_config_1 = {
            "field": "match:list/(\\d+)/name",
            "key": "two name",
        }
        test_config_2 = {
            "field": "match:two name/data/(\\d+)/name",
            "key": "sub_two",
            "return": "sub:two name/data/#0/value"
        }
        test_config_3 = {
            "field": "match:list/(\\d+)/name",
            "key": "x",
        }

        find_1 = FindIndexByKey(None, None, **test_config_1)
        find_2 = FindIndexByKey(None, None, **test_config_2)
        find_3 = FindIndexByKey(None, None, **test_config_3)

        data_obj = AccessWrapper(data)
        match = ConfWrapper.MatchAll(test_config_1, data_obj)
        self.assertEqual(len(match), 3)
        for wrapper in match:
            find_1.process(wrapper)
        self.assertEqual(data_obj['two name']['value'], 'fun')

        match = ConfWrapper.MatchAll(test_config_2, data_obj)
        self.assertEqual(len(match), 2)
        for wrapper in match:
            find_2.process(wrapper)
        self.assertEqual(data_obj['sub_two'], 'two')

        self.assertEqual(data_obj['x'], 1)
        match = ConfWrapper.MatchAll(test_config_3, data_obj)
        self.assertEqual(len(match), 3)
        for wrapper in match:
            find_3.process(wrapper)
        self.assertEqual(data_obj['x']['value'], 'x_value')


if __name__ == '__main__':
    unittest.main()