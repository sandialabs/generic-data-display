import argparse
import logging
import textwrap

from generic_data_display.utilities import config
from generic_data_display.utilities.modules_enum import ModulesEnum
from generic_data_display.utilities.logger import log

from generic_data_display.data_store import store

def _parse_args():
    """
    Setup parsing command line arguments

    :return: Parser object containing the command line option values
    """

    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""\
        The data store stores data produced by the GD2 backend for retrieval and display at a later date.
            Ex:
                gd2_data_store --config example_config.json"""))

    parser.add_argument("--config-file", dest="config_file", default=None,
                        help="Full path to config file to use for data store")
    parser.add_argument("-l", "--log-level", dest="log_level",
                        choices=["debug", "info", "trace"], default="info",
                        help="Log level to display. Options: {debug,info}")

    args = parser.parse_args()

    if not args.config_file:
        parser.error("A config file is required: --config-file")

    return args


def run():
    args = _parse_args()

    log.setLevel(getattr(logging, args.log_level.upper()))
    log.info("Starting up GD2 Data Store")

    app_config = config.load_file(args.config_file, app=ModulesEnum.DATA_STORE)
    datastore_configs = app_config['config']

    # Spin up the storage thread
    store.run(gd2_pipeline_host=datastore_configs["gd2_pipeline_host"],
            gd2_pipeline_port=datastore_configs["gd2_pipeline_port"],
            database_host=datastore_configs["database_host"],
            database_port=datastore_configs["database_port"],
            time_limit=datastore_configs["time_limit"])
