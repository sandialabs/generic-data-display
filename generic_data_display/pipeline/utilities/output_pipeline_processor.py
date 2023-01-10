import queue

from generic_data_display.pipeline.utilities.access_wrapper import ConfWrapper
from generic_data_display.pipeline.utilities.stoppable_thread import StoppableThread
from generic_data_display.utilities.logger import log


class OutputPipelinePreprocessor(StoppableThread):
    """A basic implementation of a processor class for output pipelines

    Implements the `run` method which should be similar/the same for all of the output
    pipelines. Subclasses are expected to override the 'process' method
    and 'close' method as needed. 'process' should expect to take in an AccessWrapper
    object.
    """

    def __init__(self, pop_queue, push_queue, use_conf_wrapper=True, *args, **kwargs):
        super(OutputPipelinePreprocessor, self).__init__(*args, **kwargs)
        self.pop_queue = pop_queue
        self.push_queue = push_queue
        self.use_conf_wrapper = use_conf_wrapper
        self.config = {}

    def process(self, data_object):
        pass

    def close(self):
        pass

    def run(self):
        log.info("Starting The Output Message Processor")
        try:
            while self.is_running():
                try:
                    data_object = self.pop_queue.get(block=False, timeout=None)
                    if self.use_conf_wrapper:
                        with data_object.timer(self.name):
                            self.process(ConfWrapper(data_object))
                    else:
                        self.process(data_object)
                except queue.Empty:
                    continue
        finally:
            self.close()
            log.info(self.timers.log_string)
