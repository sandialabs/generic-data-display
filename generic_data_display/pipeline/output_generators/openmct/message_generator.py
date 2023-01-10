from generic_data_display.pipeline.output_generators.openmct.dictionary_provider import add_object, root_folder_key, has_expired
import generic_data_display.pipeline.output_generators.openmct.dictionary_provider as provider
from generic_data_display.pipeline.utilities.type_wrapper import TypeWrapper

from generic_data_display.utilities.logger import log

import datetime
import copy

class UtcWrapper(TypeWrapper):
    def _omct_hints(self):
        hints = dict(
            key='utc',
            name='Time',
            format='utc',
            units='UTC',
            hints=dict(domain=1)
        )
        return {**super()._omct_hints(), **hints}


def _sanitize(omct_str):
    # TODO (ljencka): write a more comprehensize sanitization function
    return omct_str.replace('/', '.')


def generate_messages(config, data_object):
    openmct_messages = []
    data_config_copy = copy.deepcopy(config['data'])

    pass_all = config['pass_all_omct'] if 'pass_all_omct' in config else False
    max_depth = config['pass_bfs_depth'] if 'pass_bfs_depth' in config else None
    config_name = config['config_name'] if 'config_name' in config else root_folder_key
    data_timeout_sec = config['data_timeout_sec'] if 'data_timeout_sec' in config else 0

    # Used for ensuring that we don't add duplicate data
    keys = set()

    # Get configured data
    for config in data_config_copy:
        range_key = config['name'] if 'range_key' not in config else config['range_key']
        domain_key = None if 'domain_key' not in config else config['domain_key']
        config['location'] = config['location'] if 'location' in config else config_name

        try:
            range_data = data_object["key:" + range_key]
            keys.add(data_object._unalias(range_key))

            suffix = data_object.get_suffix(range_key)
            range_key = range_key + suffix
            config['name'] = config['name'] + suffix
            if domain_key:
                domain_data = data_object["key:" + domain_key]
                keys.add(data_object._unalias(domain_key))
            else:
                domain_data = UtcWrapper(
                    datetime.datetime.now().timestamp() * 1000)
                domain_key = 'utc'
        except (TypeError, KeyError):
            continue

        # Sanitize OpenMCT names and keys
        config['name'] = _sanitize(config['name'])
        domain_key = _sanitize(domain_key)
        range_key = _sanitize(range_key)

        try:
            openmct_message = {domain_key: domain_data,
                               range_key: range_data, "topic": config['name']}
        except (TypeError, KeyError):
            continue
        log.trace(f"Generated object: {openmct_message}")

        add_object(config, range_data, range_key, domain_data, config_name)
        openmct_messages.append(openmct_message)

    # Get all other OpenMCT data
    if pass_all:
        for node in data_object._bfs(max_depth=max_depth):
            if isinstance(data_object['key:' + node], TypeWrapper) and \
                    data_object._unalias(node) not in keys:
                try:
                    keys.add(data_object._unalias(node))
                    range_key = _sanitize(node)
                    range_data = data_object['key:' + node]
                    domain_data = UtcWrapper(
                        datetime.datetime.now().timestamp() * 1000)

                    openmct_message = {'utc': domain_data,
                                       range_key: range_data, "topic": range_key}
                    config = dict(name=range_key,
                                  range_key=range_key, location=config_name)

                    log.trace(f"Generated object: {openmct_message}")
                    add_object(config, range_data, range_key, domain_data, config_name)
                    openmct_messages.append(openmct_message)
                except (TypeError, KeyError):
                    continue

    if data_timeout_sec > 0:
        timeout_sec = datetime.timedelta(seconds=data_timeout_sec)
        provider.global_mct_dictionary['measurements'][:] = [val for val in
                                                             provider.global_mct_dictionary['measurements'] if
                                                             not has_expired(val, timeout_sec)]

    return openmct_messages
