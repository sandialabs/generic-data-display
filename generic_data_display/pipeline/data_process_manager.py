from generic_data_display.utilities.logger import log
from generic_data_display.pipeline import data_processor
from generic_data_display.pipeline.utilities.output_queues import OutputQueues


class DataProcessManager(object):
    def __init__(self, configs):
        self.data_processors = []
        self.output_queues = OutputQueues()
        for config in configs:
            processor = data_processor.DataProcessor(config)
            self.data_processors.append(processor)
            self.output_queues.merge(processor.output_queues)

        self.validate_configs()

    def close(self):
        for processor in self.data_processors:
            processor.close()

    def validate_configs(self):
        config_names = [c.config_name for c in self.data_processors]
        names = set()
        if any(name in names or names.add(name) for name in config_names):
            log.error(f"duplicate config name found in {config_names}, names must be unique")
            raise ValueError(f"duplicate config name: {config_names}")
