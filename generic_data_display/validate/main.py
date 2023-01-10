import argparse
import logging
import textwrap
from generic_data_display.utilities.config import load_file
from generic_data_display.utilities.modules_enum import ModulesEnum


def _parse_args():
    """
    Setup parsing command line arguments

    :return: Parser object containing the command line option values
    """

    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""\
        Validate GD2 config files for correctness."""))

    parser.add_argument("--config-file", dest="config_file", default=None,
                        help="Full path to config file to validate")
    parser.add_argument("--app", dest="app", type=ModulesEnum, choices=list(ModulesEnum),
                        default="pipeline",
                        help="App corresponding to config being validated")

    args = parser.parse_args()

    if not args.config_file:
        parser.error("A config file is required: --config-file")

    return args


def run():
    args = _parse_args()

    logging.info("Validating config file: {} for app {}".format(args.config_file, args.app))

    config = load_file(args.config_file, app=args.app)
    # config = loads(args.config_file)
