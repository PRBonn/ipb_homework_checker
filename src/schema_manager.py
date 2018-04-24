"""Manage creation of schema."""
import sys
import logging
import operator
from os import path
from tools import MAX_DATE_STR
from schema import Schema, SchemaError, Or, Optional
from schema_tags import Tags, OutputTags, BuildTags, LangTags
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
                Optional(Tags.DEADLINE_TAG,
                         default=MAX_DATE_STR): str,
                Tags.TASKS_TAG: [{
                    Tags.NAME_TAG: str,
                    Tags.LANGUAGE_TAG: Or(LangTags.CPP, LangTags.BASH),
                    Tags.FOLDER_TAG: str,
                    Optional(Tags.OUTPUT_TYPE_TAG,
                             default=OutputTags.STRING): Or(OutputTags.STRING,
                                                            OutputTags.NUMBER),
                    Optional(Tags.BINARY_NAME_TAG, default="main"): str,
                    Optional(Tags.BUILD_TYPE_TAG,
                             default=BuildTags.CMAKE): Or(BuildTags.CMAKE,
                                                          BuildTags.SIMPLE),
                    Optional(Tags.TESTS_TAG): [{
                        Tags.NAME_TAG: str,
                        Optional(Tags.INPUT_TAG): str,
                        Optional(Tags.INJECT_FOLDER_TAG): [str],
                        Optional(Tags.RUN_GTESTS_TAG, default=False): bool,
                        Optional(Tags.EXPECTED_OUTPUT_TAG): Or(str, float, int)
                    }]
                }]
            }]
        })
        yaml = YAML()
        yaml.width = 4096  # big enough value to prevent wrapping
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
            if input_var._schema == Tags.DEADLINE_TAG:
                return SchemaManager.__sanitize_value(input_var._schema)
            return '~[optional]~ ' \
                + SchemaManager.__sanitize_value(input_var._schema)
        if isinstance(input_var, Or):
            return 'Any of ' + str(
                [SchemaManager.__sanitize_value(s) for s in input_var._args])
        if input_var is str:
            return 'String value'
        if input_var is float:
            return 'Float value'
        if input_var is int:
            return 'Int value'
        if input_var is bool:
            return 'Boolean value'
        return str(input_var)
