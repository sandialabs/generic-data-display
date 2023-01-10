from generic_data_display.data_sim import data_sender

import argparse
import logging
import json
import textwrap


def _parse_args():
    """
    Setup parsing command line arguments

    :return: Parser object containing the command line option values
    """

    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""\
        The generic_data_display.data_sim sends data in a specified format over a specified connection type.
            Ex:
                generic_data_display.data_sim --config example_config.json"""))

    parser.add_argument("--config-file", dest="config_file", default=None,
                        help="Full path to config file to use for test service")
    parser.add_argument("-l", "--log-level", dest="log_level",
                        choices=["debug", "info"], default="info",
                        help="Log level to display. Options: {debug,info}")

    args = parser.parse_args()

    if not args.config_file:
        parser.error("A config file is required: --config-file")

    return args


def run():
    args = _parse_args()
    data_senders = []

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    logging.info("Starting up test service")

    logging.info("Reading json config file: {}".format(args.config_file))
    with open(args.config_file, "r") as config_file:
        config_data = json.load(config_file)
        for config in config_data["config"]:
            data_senders.append(data_sender.DataSender(config))

    logging.info("Starting data senders")
    for sender in data_senders:
        sender.run()

    logging.info("Closing data senders")
    for sender in data_senders:
        sender.close()
