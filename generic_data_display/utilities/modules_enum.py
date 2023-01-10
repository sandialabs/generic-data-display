from enum import Enum
import sys
import importlib

class ModulesEnum(Enum):
    PIPELINE = "pipeline"
    DATA_STORE = "data_store"
    DATA_SIM = "data_sim"
    VALIDATE = "validate"
    UTILITIES = "utilities"

    def __str__(self):
        return self.value

    def get_module(self):
        try:
            return sys.modules[f'generic_data_display.{self.value}']
        except KeyError as err:
            return importlib.import_module(f'generic_data_display.{self.value}')
