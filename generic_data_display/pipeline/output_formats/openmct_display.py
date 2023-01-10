from generic_data_display.pipeline.utilities.output_pipeline_processor import \
    OutputPipelinePreprocessor
from generic_data_display.pipeline.utilities.timer import TimerCollection
from generic_data_display.pipeline.web import post_namespaces

from generic_data_display.utilities.logger import log


class OpenMctDisplay(OutputPipelinePreprocessor):
    def __init__(self, pop_queue, push_queue, **kwargs):
        super().__init__(pop_queue, push_queue, False, name="Display Format Converter")
        log.info("Initializing the Open MCT Display Output Processor")

        self.config = dict(
            print_timing=False
        )
        self.config.update(kwargs)
        self.pop_queue = pop_queue
        self.push_queue = push_queue
        self.timers = TimerCollection(self.config['print_timing'], 1000)

    def close(self):
        log.info("Shut down Open MCT Display Output Processor")

    def process(self, data_object):
        self.push_queue.put(data_object)
