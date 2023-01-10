import unittest

from generic_data_display.pipeline.preprocessors.omct_hints import OmctHints
from generic_data_display.pipeline.utilities.access_wrapper import ConfWrapper
from generic_data_display.pipeline.utilities.type_wrapper import TypeWrapper

from generic_data_display.utilities.logger import log



class TestOmctHints(unittest.TestCase):
    test_app_config = {
        "description": "Test",
        "version": "1.0",
        "config": []
    }

    test_config = dict(
        confs = [
            dict(match="key:alpha", hints=dict(units="things")),
            dict(match="key:delta", hints=dict(units="hmm", format="float")),
            dict(match="key:notused", hints=dict(units="???", format="int")),
        ]
    )
 
    def test_omct_hints(self):
        log.setLevel("TRACE")

        proc = OmctHints(None, None, config_name="test_config", **self.test_config)

        data = ConfWrapper({"alpha": [1,2,3,4], "beta": True, "delta": "cool"})

        proc.process(data)

        self.assertIsInstance(data['key:alpha'], TypeWrapper)
        self.assertEqual(data['key:alpha']._omct_hints(), dict(units="things"))

        self.assertNotIsInstance(data['key:beta'], TypeWrapper)

        self.assertIsInstance(data['key:delta'], TypeWrapper)
        self.assertEqual(data['key:delta']._omct_hints(), dict(units="hmm", format="float"))

        self.assertNotIn("notused", data.keys())


if __name__ == '__main__':
    unittest.main()