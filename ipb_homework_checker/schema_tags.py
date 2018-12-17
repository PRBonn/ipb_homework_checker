"""Collection of schema related tags."""


class Tags:
    """List of tags available."""
    BINARY_NAME_TAG = 'binary_name'
    BUILD_TYPE_TAG = 'build_type'
    COMPILER_FLAGS_TAG = 'compiler_flags'
    DEADLINE_TAG = 'submit_by'
    EXPECTED_OUTPUT_TAG = 'expected_output'
    FOLDER_TAG = 'folder'
    HOMEWORKS_TAG = 'homeworks'
    INJECT_FOLDER_TAG = 'inject_folders'
    INPUT_TAG = 'input_args'
    LANGUAGE_TAG = 'language'
    NAME_TAG = 'name'
    OUTPUT_TYPE_TAG = 'output_type'
    PIPE_TAG = 'pipe_through'
    RUN_GTESTS_TAG = 'run_google_tests'
    TASKS_TAG = 'tasks'
    TESTS_TAG = 'tests'


class OutputTags:
    """Define tags for output types."""
    STRING = 'string'
    NUMBER = 'number'
    ALL = [STRING, NUMBER]


class BuildTags:
    """Define tags for build types."""
    CMAKE = 'cmake'
    SIMPLE = 'simple'
    ALL = [CMAKE, SIMPLE]


class LangTags:
    """Define tags for build types."""
    CPP = 'cpp'
    BASH = 'bash'
    ALL = [CPP, BASH]


class OneOf:
    """Check that an item is one of the list."""

    def __init__(self, some_list):
        """Set the list to choose from."""
        self.__items = some_list

    def __call__(self, item):
        """Check that the list contains what is needed."""
        return item in self.__items

    def __str__(self):
        """Override str for this class."""
        return "Possible values: {}".format(self.__items)
