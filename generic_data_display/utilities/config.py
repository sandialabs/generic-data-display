import json
import os

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from jsonschema import RefResolver
from jsonschema.validators import validator_for

import generic_data_display
from generic_data_display.utilities.modules_enum import ModulesEnum

def _load_schemas(app):
    schemas = {}
    schemas['base_schema.jsonschema'] = json.loads(files(generic_data_display).joinpath("resources/base_schema.jsonschema").read_bytes())
    for root, _, _files in os.walk(files(app.get_module()).joinpath("resources/json_schemas")):
        for file in _files:
            with open(root + os.sep + file) as schema_file:
                schemas[file] = json.loads(schema_file.read())
    return schemas

def _create_validator(app):
    schemas = _load_schemas(app)
    base_schema = schemas.pop('base_schema.jsonschema')
    resolver = RefResolver.from_schema(base_schema, store=schemas)
    Validator = validator_for(base_schema)
    validator = Validator(schemas[f'{app.value}.jsonschema'], resolver=resolver)
    return validator

def load_file(json_file, app=ModulesEnum.PIPELINE):
    with open(json_file, 'r') as f:
        config = json.load(f)
    validator = _create_validator(app)
    validator.validate(config)
    return config

def loads(json_str, app=ModulesEnum.PIPELINE):
    if type(json_str) == str:
        config = json.loads(json_str)
    elif type(json_str) == dict:
        converted_json_str = json.dumps(json_str)
        config = json.loads(converted_json_str)
    validator = _create_validator(app)
    validator.validate(config)
    return config
