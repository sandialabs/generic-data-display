import unittest

import generic_data_display.pipeline.tests


def load_tests(loader, tests, pattern):
    return loader.discover('.')


def run():
    unittest.main()


if __name__ == "__main__":
    unittest.main()
