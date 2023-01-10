import csv

from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.utilities.timer import Timer
from generic_data_display.pipeline.utilities.access_wrapper import AccessWrapper


class CSVParser(object):
    """
    CSV Parser!

    """
    def __init__(self, push_queue, **kwargs):
        log.info("Initializing the CSV Parser")

        self.push_queue = push_queue
        self.config = {}
        self.config.update(kwargs)
        self.iter = None
        self.headers = self.config['csv_headers'].split(',')
        self.buffer = ""

    def int_or_float(self, val):
        # is.numeric() will evaluate integers in a string just fine but doesn't work for floats
        if val.isnumeric():
            val = int(val)
        else:
            try:
                val = float(val)
            except:
                pass
        return val

    def reset_io_byte_stream(self):
        pass

    def parse_io_byte_stream(self, io_stream):
        self.buffer += io_stream.read(1024).decode()
        while '\n' in self.buffer:
            timer = Timer()
            with timer('CSV Parser'):
                csv_str, self.buffer = self.buffer.split('\n', 1)
                records = csv_str.split(',')
                msg = {self.headers[i]: records[i] for i in range(len(self.headers))}
                for key, val in msg.items():
                    msg[key] = self.int_or_float(val)
                self.push_queue.put(AccessWrapper(msg, timer=timer))

    def parse_from_bytes(self, obj_bytes):
        timer = Timer()
        with timer('CSV Parser'):
            records = obj_bytes.decode().split(',')
            msg = {self.headers[i]: records[i] for i in range(len(self.headers))}
            for key, val in msg.items():
                msg[key] = self.int_or_float(val)
            self.push_queue.put(AccessWrapper(msg, timer=timer))
