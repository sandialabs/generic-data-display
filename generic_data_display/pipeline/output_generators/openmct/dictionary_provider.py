from generic_data_display.pipeline.utilities.type_wrapper import TypeWrapper
from generic_data_display.utilities.logger import log

import datetime

root_folder_key = "root-object"
global_mct_dictionary = {
    "measurements": []
}

global_mct_namespaces = []

def has_expired(measurement, timeout_sec):
    if 'data' in measurement['type']:
        if datetime.datetime.now() > datetime.datetime.fromtimestamp(measurement['last_updated']) + timeout_sec:
            log.info(f"measurement {measurement['name']} has expired")
            return True
    return False

def generate_root_namespaces(config):
    root_namespaces = []

    if config['config_name'] not in root_namespaces:
        global_mct_dictionary["measurements"].append(
                                                dict(
                                                    key=config['config_name'],
                                                    name=config['config_name'],
                                                    type="folder",
                                                    location="ROOT",
                                                    composition=[]
                                                )
                                            )

    global_mct_namespaces.append(config['config_name'])

def generate_composition(config):
    for data in config['data']:
        if 'type' not in data:
            continue
        if data['type'] == "layout":
            location = data['location'] if 'location' in data else config['config_name']
            create_layout(config, data, location)
        if data['type'] == "folder":
            location = data['location'] if 'location' in data else config['config_name']
            create_folder(data['name'], config['config_name'], location=location)


def create_layout(config, data, location):
    location = get_item(location)
    if not location:
        log.error(f"location {location} for new layout {data['name']} did not exist, defaulting to root")
        location = get_item(root_folder_key)
    composition = _create_layout_composition(config['config_name'], data['format'])
    configuration = _create_layout_configuration(config['config_name'], data)
    _create_mct_layout(data['name'], config['config_name'], location, composition, configuration)


def create_folder(folder_key, namespace_key, location=root_folder_key):
    parent_folder = get_item(location)
    if not parent_folder:
        log.error(f"location {location} for new folder {folder_key} did not exist, defaulting to root")
        parent_folder = get_item(root_folder_key)
    _create_mct_folder(folder_key, namespace_key, parent_folder)


def get_item(item_key):
    measurements = global_mct_dictionary['measurements']
    try:
        return next(match for match in measurements if match['key'] == item_key)
    except StopIteration:
        return None


def _create_layout_composition(namespace_key, layout_format):
    composition = []
    for rows in layout_format:
        for col in rows:
            composition.append(_create_identifier(namespace_key, col))
    return composition


def _create_layout_configuration(namespace_key, data):
    layout_format = data['format']
    configuration = dict(containers=list(),
                         rowsLayout=data['rowsLayout'] if 'rowsLayout' in data else True)
    if layout_format:
        row_size = 100 / len(layout_format)
        for i, row in enumerate(layout_format, start=1):
            container = dict(id=f"container{i}",
                             frames=list(),
                             size=int(row_size))
            if row:
                col_size = 100 / len(row)
                for j, col in enumerate(row, start=1):
                    frame = dict(id=f"{container['id']}-frame{j}",
                                 domainObjectIdentifier=_create_identifier(namespace_key, col),
                                 noFrame=False,
                                 size=int(col_size))
                    container['frames'].append(frame)
            configuration['containers'].append(container)
    return configuration


def _create_mct_folder(folder_key, namespace_key, parent_folder):
    folder = get_item(folder_key)
    if folder:
        log.debug(f"supplied folder_key '{folder_key}' exists already, doing nothing: {folder}")
        return
    _add_composition_to_item(parent_folder, folder_key, namespace_key)
    global_mct_dictionary['measurements'].append(dict(
        key=folder_key,
        namespace=namespace_key,
        name=folder_key,
        type="folder",
        location=f"{namespace_key}:{parent_folder['key']}",
        composition=[]
    ))


def _create_mct_layout(layout_key, namespace_key, parent_folder, composition, configuration):
    layout = get_item(layout_key)
    if layout:
        log.debug(f"supplied layout_key '{layout_key}' exists already, doing nothing: {layout}")
        return
    _add_composition_to_item(parent_folder, layout_key, namespace_key)
    global_mct_dictionary['measurements'].append(dict(
        key=layout_key,
        namespace=namespace_key,
        name=layout_key,
        type="flexible-layout",
        location=f"{namespace_key}:{parent_folder['key']}",
        composition=composition,
        configuration=configuration
    ))

def _add_composition_to_item(item, obj_key, namespace_key):
    if not item or (item and 'composition' not in item):
        log.error(f"Attempted to add key '{obj_key}' to item without composition: {item}, defaulting to root")
        item = get_item(root_folder_key)
    item['composition'].append(_create_identifier(namespace_key, obj_key))
    log.debug(f"updated object composition: {item}")


def _create_identifier(namespace_key, obj_key):
    return dict(
        namespace=namespace_key,
        key=obj_key
    )


def add_object(config, omct_range_data, range_key, omct_domain_data, namespace_key):
    measurements = global_mct_dictionary['measurements']
    location = config['location'] if 'location' in config else root_folder_key

    if any(measurement['name'] == config['name'] for measurement in measurements):
        return

    new_measurement = _type_obj_to_mct(config, omct_range_data, range_key, omct_domain_data, location, namespace_key)
    global_mct_dictionary['measurements'].append(new_measurement)
    log.debug(f"added new measurement: {new_measurement}")


def _type_obj_to_mct(config, omct_range_data, range_key, omct_domain_data, location, namespace_key):
    values = []
    mct_type = "plot.data"

    range_value = dict(
        key=range_key,
        name=range_key,
        format=config['format'] if 'format' in config else None,
        units=config['units'] if 'units' in config else None,
        hints=dict(range=1)
    )
    if isinstance(omct_range_data, TypeWrapper):
        range_value.update(omct_range_data._omct_hints())
        if range_value['format'] == 'image':
            mct_type = "image.data"

    values.append(range_value)

    domain_value = dict(
        key='utc',
        name='Timestamp',
        format='utc',
        units='UTC',
        hints=dict(domain=1)
    )

    if isinstance(omct_range_data, TypeWrapper):
        domain_value.update(omct_domain_data._omct_hints())

    values.append(domain_value)

    _add_composition_to_item(get_item(location), config['name'], namespace_key)
    return dict(name=config['name'],
                namespace=namespace_key,
                key=config['name'],
                location=f"{namespace_key}:{location}",
                type=mct_type,
                last_updated=datetime.datetime.now().timestamp(),
                telemetry=dict(values=values))
