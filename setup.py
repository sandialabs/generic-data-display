#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as fh:
    install_requires = fh.read().splitlines()

with open('version.txt', 'r') as fh:
    version_string = fh.read()

setup(
    name='generic_data_display',
    version=version_string,
    description='Generic and configurable streaming data visualizer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='[ADD_NEW_GITHUB_URL_HERE]',
    packages=find_packages(),
    include_package_data=True,
    package_data={'generic_data_display': ['resources/*.jsonschema'],
                  'generic_data_display.pipeline': ['resources/json_schemas/**/*.jsonschema',
                                                    'resources/json_schemas/*.jsonschema',
                                                    'resources/json_schemas/**/**/*.jsonschema'],
                  'generic_data_display.data_store': ['resources/json_schemas/*.jsonschema']},
    entry_points={
        "console_scripts": [
            "gd2_tests=generic_data_display.pipeline.tests.__main__:run",
            "gd2_pipeline=generic_data_display.pipeline.main:run",
            "gd2_data_sim=generic_data_display.data_sim.main:run",
            "gd2_data_store=generic_data_display.data_store.main:run",
            "gd2_validate=generic_data_display.validate.main:run"
        ]
    },
    setup_requires=[
        'pip>=9.0.0',
        'wheel'
    ],
    install_requires=install_requires,
    data_files=[("", ["LICENSE.txt"])],
)
