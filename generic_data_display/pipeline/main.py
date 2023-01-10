import logging
import aiohttp
import argparse
import textwrap

from generic_data_display.pipeline import websocket

from generic_data_display.pipeline import data_process_manager
from generic_data_display.pipeline import web

from generic_data_display.utilities.logger import log
from generic_data_display.utilities import config


def _parse_args():
    """
    Setup parsing command line arguments

    :return: Parser object containing the command line option values
    """

    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""\
        The generic_data_display is an application that takes streaming data over an input connection
        and forwards pre-processed data in a standardized format for display on a corresponding front-end
        application.
            Ex:
                generic_data_display --config app_config.json"""))

    parser.add_argument("--config-file", dest="config_file", default=None,
                        help="Full path to config file to use for test service")
    parser.add_argument("-l", "--log-level", dest="log_level",
                        choices=["debug", "info", "trace"], default="info",
                        help="Log level to display. Options: {debug,info}")
    parser.add_argument("-p", "--http-port", dest="http_port",
                        default=8844, help="The port to use for the http web app")

    args = parser.parse_args()

    if not args.config_file:
        parser.error("A config file is required: --config-file")

    return args


def run():
    # Parse and load configs
    args = _parse_args()
    log.setLevel(getattr(logging, args.log_level.upper()))
    log.info("Starting up Generic Data Display")

    app_config = config.load_file(args.config_file)

    # Setup WS manager
    websocket_manager = websocket.WebsocketManager()

    # Setup data processors
    process_manager = data_process_manager.DataProcessManager(
        app_config['config'])
    websocket_manager.add_output_queues(
        process_manager.output_queues['openmct_display'])

    # Setup and run AIOHTTP server
    app = web.create_app(websocket_manager, process_manager)
    aiohttp.web.run_app(app, port=args.http_port,
                        shutdown_timeout=30.0)
