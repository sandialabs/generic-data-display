import base64
import logging
from io import BytesIO
from collections import namedtuple

from PIL import Image

from generic_data_display.pipeline.utilities.basic_preprocessor import BasicPreprocessor
from generic_data_display.pipeline.utilities.type_wrapper import TypeWrapper

_Fmt = namedtuple('Fmt', ('channels'))
_FORMAT_INFO = {
    'RGB': _Fmt(channels=3)
}


class ImageUri(TypeWrapper):
    def _omct_hints(self):
        hints = dict(
            format='image',
            type='image',
            hints=dict(image=1)
        )
        return {**super()._omct_hints(), **hints}


class Imagify(BasicPreprocessor):
    """
    inputs:
    - input_array: An array of image data

    outputs:
    - datauri: a base64 encoded image data URI

    config:
    - input_format: see pillow image types (default: rgb)
    - datauri_format: image format for the output datauri (default: TIFF)
    - width: input image width
    - height: input image height
    """

    def __init__(self, pop_queue, push_queue, **kwargs):
        super().__init__(pop_queue, push_queue, name="Imagify")

        # default values
        self.config = dict(
            input_format='RGB',
            datauri_format='BMP'
        )

        self.config.update(kwargs)

        if 'log_level' in self.config:
            logging.getLogger('PIL').setLevel(getattr(logging, self.config['log_level'].upper()))

    def process(self, data_obj):
        if self.config['input_format'] not in _FORMAT_INFO.keys():
            raise ValueError(
                f"Provided input format {self.config['input_format']} "
                f"was not found in: {_FORMAT_INFO.keys()}")

        fmt = _FORMAT_INFO[self.config['input_format']]
        size = (data_obj[self.config['rows']], data_obj[self.config['cols']])

        if len(data_obj[self.config['input_array']]) != size[0] * size[1] * fmt.channels:
            raise ValueError(
                f"Provided data size {len(data_obj[self.config['input_array']])} "
                f"did not match the configured size {size[0] * size[1] * fmt.channels}")

        with Image.frombytes(self.config['input_format'], size, data_obj[self.config['input_array']],
                             "raw", self.config['input_format'], 0, 1) as image:
            data_obj[self.config['datauri']] = ImageUri(self.image_to_uri(image))

    def image_to_uri(self, image):
        if self.config['datauri_format'] != 'BMP':
            raise ValueError(
                f"Provided datauri_format {self.config['datauri_format']} "
                f"is not supported; please select from the supported types: [BMP]")

        buffer = BytesIO()
        image.save(buffer, self.config['datauri_format'])
        data64 = base64.b64encode(buffer.getvalue())
        return f'data:img/bmp;base64,{data64.decode("utf-8")}'
