"""Manage creation of schema."""
import sys
import logging
from os import path
from schema import Schema, SchemaError, Or, Optional
from ruamel.yaml import YAML
from tools import OneOf

log = logging.getLogger("GHC")

SCHEMA_FILE = path.join(path.dirname(
    path.dirname(__file__)), "schema", "schema.yml")


class Tags:
    """List of tags available."""
    BASE_TAG = 'base_node'
    NAME_TAG = 'name'
    TESTS_TAG = 'tests'
    FOLDER_TAG = 'folder'
    INPUT_TAG = 'input_args'
    LANGUAGE_TAG = 'language'
    OUTPUT_TAG = 'expected_output'
    BINARY_NAME_TAG = 'binary_name'
    OUTPUT_TYPE_TAG = 'output_type'
    EXERCISES_TAG = 'exercises'


class OutputTags:
    """Define tags for output types."""
    STRING = 'string'
    NUMBER = 'number'
    ALL = [STRING, NUMBER]


class SchemaManager:
    """Manage schema creation."""

    def __init__(self, file_name):
        """Create a schema for my tests."""
        self.__schema = Schema(
            {
                Tags.FOLDER_TAG: str,
                Tags.EXERCISES_TAG: [
                    {
                        Tags.NAME_TAG: str,
                        Tags.LANGUAGE_TAG: str,
                        Tags.FOLDER_TAG: str,
                        Tags.OUTPUT_TYPE_TAG: OneOf(OutputTags.ALL),
                        Optional(Tags.INPUT_TAG): str,
                        Optional(Tags.BINARY_NAME_TAG, default="main"): str,
                        Tags.TESTS_TAG: [
                            {
                                Tags.NAME_TAG: str,
                                Tags.OUTPUT_TAG: Or(str, float, int),
                                Optional(Tags.INPUT_TAG): str
                            }
                        ]
                    }
                ]
            })
        yaml = YAML()
        with open(file_name, 'r') as stream:
            contents = yaml.load(stream)
            try:
                self.__validated_yaml = self.__schema.validate(contents)
            except SchemaError as exc:
                sys.exit(exc.code)
        # Write the schema every time we run this code.
        with open(SCHEMA_FILE, 'w') as outfile:
            str_dict = SchemaManager.__sanitize_value(
                self.__schema._schema)
            yaml.dump(str_dict, outfile)

    @property
    def validated_yaml(self):
        """Return validated yaml."""
        return self.__validated_yaml

    @property
    def schema(self):
        """Return schema."""
        return self.__schema

    @staticmethod
    def __sanitize_value(input_var):
        """Use the schema and create an example file from it."""
        if isinstance(input_var, dict):
            new_dict = {}
            for key, val in input_var.items():
                new_dict[SchemaManager.__sanitize_value(key)] \
                    = SchemaManager.__sanitize_value(val)
            return new_dict
        if isinstance(input_var, list):
            new_list = []
            for val in input_var:
                new_list.append(SchemaManager.__sanitize_value(val))
            return new_list
        if isinstance(input_var, Optional):
            return str(input_var._schema)
        return str(input_var)
