import unittest

import urllib.request
import numpy
from io import BytesIO
from PIL import Image

from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.preprocessors.imagify import Imagify
from generic_data_display.pipeline.utilities.access_wrapper import ConfWrapper, AccessWrapper


class MyTestCase(unittest.TestCase):
    def test_imagify(self):
        log.setLevel("TRACE")
        test_image = Image.fromarray((numpy.random.rand(64, 64, 3) * 255).astype('uint8')).convert('RGB')
        test_bytes = test_image.tobytes()
        buffer = BytesIO()
        test_image.save(buffer, "BMP")
        data = {
            'image': test_bytes,
            'image_edge': 64,
            'bad_row': 13
        }
        good_config = {
            "input_array": "image",
            "datauri": "url",
            "rows": "image_edge",
            "cols": "image_edge"
        }
        imagify = Imagify(None, None, **good_config)
        data_obj = AccessWrapper(data)

        imagify.process(data_obj)
        self.assertIsNotNone(data_obj['url'])
        image = urllib.request.urlopen(data_obj['url'])
        self.assertEqual(image.file.read(), buffer.getvalue())

    def test_imagify_bad(self):
        log.setLevel("TRACE")
        test_image = Image.fromarray((numpy.random.rand(64, 64, 3) * 255).astype('uint8')).convert('RGB')
        test_bytes = test_image.tobytes()
        buffer = BytesIO()
        test_image.save(buffer, "BMP")
        data = {
            'image': test_bytes,
            'image_edge': 64,
            'bad_row': 13
        }
        bad_config = {
            "input_array": "image",
            "datauri": "url",
            "rows": "bad_row",
            "cols": "bad_col"
        }
        data_obj = AccessWrapper(data)

        imagify = Imagify(None, None, **bad_config)
        self.assertRaises(KeyError, imagify.process, data_obj)

        bad_config['cols'] = 'image_edge'
        imagify = Imagify(None, None, **bad_config)
        self.assertRaises(ValueError, imagify.process, data_obj)

        bad_config['cols'] = 'image_edge'
        data['image'] = 'junk_data'
        data_obj = AccessWrapper(data)
        imagify = Imagify(None, None, **bad_config)
        self.assertRaises(ValueError, imagify.process, data_obj)


if __name__ == '__main__':
    unittest.main()
