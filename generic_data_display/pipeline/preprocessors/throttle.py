from generic_data_display.pipeline.utilities.basic_preprocessor import BasicPreprocessor
from generic_data_display.utilities.logger import log

import datetime


class Throttler(BasicPreprocessor):
    """Manually Drop data for a specific field to "throttle" what is sent to the frontend

    This Preprocessor takes a list of named input config fields and deletes them from the
    forwarded object if not enough time has passed since a previous field was last sent.
    This preprocessor can be useful in rate limiting image data, or even certain
    types of dense fields that don't necessarily need updating at the input data rate.
    """

    def __init__(self, pop_queue, push_queue, **kwargs):
        super().__init__(pop_queue, push_queue, name="Throttle")

        self.config = kwargs

        self.last_time_sent = datetime.datetime.min
        self.time_delta = datetime.timedelta(milliseconds=self.config['throttle_rate_ms'])

    def process(self, data_object):
        if datetime.datetime.now() > self.last_time_sent + self.time_delta:
            self.last_time_sent = datetime.datetime.now()
        else:
            for field in self.config['fields']:
                data_object.throttle(field)
