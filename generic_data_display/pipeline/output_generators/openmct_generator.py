from generic_data_display.pipeline.output_generators.openmct.dictionary_provider import \
    generate_composition, generate_root_namespaces
from generic_data_display.pipeline.output_generators.openmct.message_generator import \
    generate_messages
from generic_data_display.pipeline.utilities.output_pipeline_processor import \
    OutputPipelinePreprocessor
from generic_data_display.pipeline.utilities.timer import TimerCollection
from generic_data_display.pipeline.web import post_namespaces

from generic_data_display.utilities.logger import log


class OpenMctGenerator(OutputPipelinePreprocessor):
    def __init__(self, pop_queue, push_queue, **kwargs):
        super().__init__(pop_queue, push_queue, name="Display Format Converter")
        log.info("Initializing the Open MCT Message Generator")

        self.config = dict(
            print_timing=False
        )
        self.config.update(kwargs)
        self.pop_queue = pop_queue
        self.push_queue = push_queue
        self.timers = TimerCollection(self.config['print_timing'], 1000)

        generate_root_namespaces(self.config)
        if 'local_testing' not in kwargs:
            post_namespaces()
        generate_composition(self.config)

    def close(self):
        log.info("Shut down Open MCT Message Generator")

    def process(self, data_object):
        openmct_messages = generate_messages(self.config, data_object)
        for message in openmct_messages:
            self.push_queue.put(message)
