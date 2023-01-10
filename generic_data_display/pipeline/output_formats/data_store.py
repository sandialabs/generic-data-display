import zmq
from generic_data_display.pipeline.utilities.output_pipeline_processor import \
    OutputPipelinePreprocessor
from generic_data_display.pipeline.utilities.timer import TimerCollection
from generic_data_display.pipeline.utilities.type_wrapper import JSONEncoder

from generic_data_display.utilities.logger import log


class DataStore(OutputPipelinePreprocessor):
    def __init__(self, pop_queue, push_queue, **kwargs):
        super().__init__(pop_queue, push_queue, False, name="Data Store Display Format Converter")
        log.info("Initializing the Data Store Message Processor")

        self.config = dict(
            print_timing=False
        )
        self.config.update(kwargs)
        self.pop_queue = pop_queue
        self.push_queue = push_queue
        self.timers = TimerCollection(self.config['print_timing'], 1000)
        self.data_store_host = self.config['data_store_host']
        self.data_store_port = self.config['data_store_port']
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(
            "tcp://{}:{}".format(self.data_store_host, self.data_store_port))
        self._encoder = JSONEncoder()

        log.info("Bound socket: {}".format(self.socket.get(zmq.IDENTITY)))

    def close(self):
        self.socket.close()
        self.context.destroy()
        log.info("Shut Down Data Store Message Processor")

    def process(self, data_object):
        self.socket.send_string(self._encoder.encode(data_object))
