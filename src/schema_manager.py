"""Manage creation of schema."""
import sys
import logging
import operator
from os import path
from schema import Schema, SchemaError, Or, Optional
from schema_tags import Tags, OutputTags, BuildTags, LangTags, OneOf
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

log = logging.getLogger("GHC")

SCHEMA_FILE = path.join(path.dirname(
    path.dirname(__file__)), "schema", "schema.yml")


class SchemaManager:
    """Manage schema creation."""

    def __init__(self, file_name):
        """Create a schema for my tests."""
        self.__schema = Schema({
            Tags.FOLDER_TAG: str,
            Tags.HOMEWORKS_TAG: [{
                Tags.NAME_TAG: str,
                Tags.FOLDER_TAG: str,
                Tags.TASTS_TAG: [{
                    Tags.NAME_TAG: str,
                    Tags.LANGUAGE_TAG: OneOf(LangTags.ALL),
                    Tags.FOLDER_TAG: str,
                    Optional(Tags.OUTPUT_TYPE_TAG,
                             default=OutputTags.STRING): OneOf(OutputTags.ALL),
                    Optional(Tags.INPUT_TAG): str,
                    Optional(Tags.BINARY_NAME_TAG, default="main"): str,
                    Optional(Tags.BUILD_TYPE_TAG,
                             default=BuildTags.CMAKE): OneOf(BuildTags.ALL),
                    Optional(Tags.TESTS_TAG): [{
                        Tags.NAME_TAG: str,
                        Tags.OUTPUT_TAG: Or(str, float, int),
                        Optional(Tags.INPUT_TAG): str
                    }]
                }]
            }]
        })
        yaml = YAML()
        yaml.explicit_start = True
        yaml.indent(mapping=2, sequence=4, offset=2)
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
            return CommentedMap(
                sorted(new_dict.items(), key=operator.itemgetter(0)))
        if isinstance(input_var, list):
            new_list = []
            for val in input_var:
                new_list.append(SchemaManager.__sanitize_value(val))
            return new_list
        if isinstance(input_var, Optional):
            return '~[optional]~ ' + str(input_var._schema)
        return str(input_var)
