from generic_data_display.pipeline.utilities.basic_preprocessor import BasicPreprocessor
from generic_data_display.utilities.logger import log


class FindIndexByKey(BasicPreprocessor):
    """Takes a supplied list of matching expressions and finds the matches for those fields
    """

    def __init__(self, pop_queue, push_queue, **kwargs):
        super().__init__(pop_queue, push_queue, name="FindIndexByKey")
        log.info("Initializing the FindIndexByKey preprocessor")

        self.config = dict()
        self.config.update(kwargs)

    def process(self, data_object):
        field = data_object[self.config['field']]
        if field != self.config['key']:
            return

        return_string = self.config['return'] if 'return' in self.config else \
            'key:' + data_object.get_match().rsplit("/", 1)[0]
        data_object[self.config['key']] = data_object[return_string]
