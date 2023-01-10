from generic_data_display.pipeline.utilities.basic_preprocessor import BasicPreprocessor


class FieldAverage(BasicPreprocessor):
    def __init__(self, pop_queue, push_queue, **kwargs):
        super().__init__(pop_queue, push_queue, name="Average")

        self.config = kwargs

    def close(self):
        pass

    def process(self, data_object):
        pass
