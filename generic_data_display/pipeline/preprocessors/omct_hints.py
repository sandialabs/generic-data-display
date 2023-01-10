from copy import deepcopy

from generic_data_display.pipeline.utilities.basic_preprocessor import BasicPreprocessor
from generic_data_display.pipeline.utilities.type_wrapper import TypeWrapper

from generic_data_display.utilities.logger import log


class TypeHints(TypeWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._self_hints = dict()

    def _omct_hints(self):
        return {**super()._omct_hints(), **self._self_hints}


class OmctHints(BasicPreprocessor):
    """
    inputs:
    - confs: {
        - match: a "key:" or "match:" for matching an entry in the pipeline object
        - hints: a dictionary of hints to pass to the OpenMCT frontend
       }

    example: [
        {
            "match": "key:stream0",
            "hints": { "units": "pixels" }
        }
    ]
    """

    def __init__(self, pop_queue, push_queue, **kwargs):
        super().__init__(pop_queue, push_queue, name="OmctHints")

        # default values
        self.config = dict(omct=[])
        self.config.update(kwargs)

    def process(self, data_obj):
        for conf in self.config['confs']:
            try:
                obj = TypeHints(data_obj[conf["match"]])
                obj._self_hints = deepcopy(conf["hints"])
                data_obj[conf["match"]] = obj
            except KeyError:
                continue
            except TypeError:
                continue