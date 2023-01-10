from generic_data_display.pipeline.utilities.basic_preprocessor import BasicPreprocessor
from generic_data_display.utilities.logger import log


class SplitByKey(BasicPreprocessor):
    """Takes values associated with key input fields and generates new output fields with different representative
       names dependent on the values of the key fields from the input data set.

       This preprocessor takes a list of dictionaries describing the input field key names to sort by,
       supporting optional value ranges for keys whose split fields are discrete, an optional list of
       field names to apply the renaming scheme to, and an optional argument specifying the rate at which
       to clear stale topics exposed to OpenMCT (in the case of ephemeral key values). When a list of
       field names to apply the renaming to is not provided all available topic names will be modified.
       When the clear stale topic rate argument is not provided the fields will be kept around until
       exit.

       Example:
        input: {stream_id: x, rows: i, cols: j, imgData: blob}
        splitByKey: {"key_fields": {"stream_id": [0,1,2]}, "value_fields": ["imgData"], "delimiter": "_"}
        output: {stream_id: 0, rows: 64, cols: 64, imgData_0: blob} ... {stream_id: 2, rows: 128, cols: 128, imgData_2: blob}
    """

    def __init__(self, pop_queue, push_queue, **kwargs):
        super().__init__(pop_queue, push_queue, name="SplitByKey")

        self.config = dict(
            key_delimiter=':'
        )
        self.config.update(kwargs)
        self.name_suffix = ''

    def process(self, data_object):
        if data_object.is_split:
            log.warning("split_by_key was called twice on data object. Currently only one split_by_key "
                        "is allowed per pipeline. Skipping.")
            return

        evaluated_keys = ['']
        for key_field, values in self.config['key_fields'].items():
            key_value = data_object[key_field]
            if not self.verify_key_value(key_value, values):
                log.warning(f"Found key '{key_field}' whose value '{key_value}' was not in '{values}', skipping")
                continue
            evaluated_keys.append(str(key_value))

        self.set_field_suffix(self.config['key_delimiter'], evaluated_keys)
        log.trace(f"evaluated keys: {evaluated_keys}, name_suffix: {self.name_suffix}")

        if 'value_fields' in self.config and self.config['value_fields']:
            for field in self.config['value_fields']:
                data_object.split(field, self.name_suffix)
        else:
            data_object.split_all(self.name_suffix)

    @staticmethod
    def verify_key_value(key_value, accepted_values):
        if not accepted_values:
            return True
        return key_value in accepted_values

    def set_field_suffix(self, delimiter, evaluated_keys):
        self.name_suffix = delimiter.join(evaluated_keys)
