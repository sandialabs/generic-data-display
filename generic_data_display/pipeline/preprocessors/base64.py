import base64

from generic_data_display.pipeline.utilities.basic_preprocessor import BasicPreprocessor
from generic_data_display.utilities.logger import log


class Base64(BasicPreprocessor):
    """
    inputs:
    - input: Data to encode/decode as Base64

    outputs:
    - output: key for processed data

    config:
    - operation: "encode" or "decode"
    """

    def __init__(self, pop_queue, push_queue, **kwargs):
        super().__init__(pop_queue, push_queue, name="Base64")

        self.config.update(kwargs)

    def process(self, data_obj):
        if self.config['operation'] == 'encode':
            data_obj[self.config['output']] = base64.b64encode(data_obj[self.config['input']])
        elif self.config['operation'] == 'decode':
            data_obj[self.config['output']] = base64.b64decode(data_obj[self.config['input']])
        else:
            log.error(f"Unknown operation '{self.config['operation']}'")
