import queue
import json

import ijson
from jsonschema import validate, ValidationError

from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.utilities.timer import Timer
from generic_data_display.pipeline.utilities.access_wrapper import AccessWrapper


class JsonParser(object):
    """
    JSON Parser!

    Config:
        - schema: path to a json schema file
    """

    def __init__(self, push_queue, **kwargs):
        log.info("Initializing the Json Parser")

        self.push_queue = push_queue
        self.config = {}
        self.config.update(kwargs)
        self.iter = None

        self.schema = None
        if "schema" in self.config.keys():
            with open(self.config["schema"], 'r') as handle:
                self.schema = json.load(handle)

    def _validate(self, json_msg):
        if self.schema:
            try:
                validate(instance=json_msg, schema=self.schema)
            except ValidationError:
                log.warn("JSON msg failed validation")
                log.debug(f"Bad json message: {json_msg}")
                return False
        return True

    def reset_io_byte_stream(self):
        self.iter = None

    def parse_io_byte_stream(self, io_stream):
        if self.iter is None:
            self.iter = ijson.items(io_stream, '', multiple_values=True)
        timer = Timer()
        with timer('Json Parser (from byte stream)'):
            msg = next(self.iter)
            if self._validate(msg):
                self.push_queue.put(AccessWrapper(msg, timer=timer))

    def parse_from_bytes(self, obj_bytes):
        timer = Timer()
        with timer('Json Parser (from bytes)'):
            msg = json.loads(obj_bytes)
            if not self._validate(msg):
                return
            self.push_queue.put(AccessWrapper(msg, timer=timer))

