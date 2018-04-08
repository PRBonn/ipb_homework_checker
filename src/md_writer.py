"""Write test results into a markdown file."""


TABLE_TEMPLATE = "| {hw_name} | {ex_name} | {test_name} | {result_sign} |\n"
TABLE_SEPARATOR = "|---|---|---|:---:|\n"

ERROR_TEMPLATE = """- `[{hw_name}][{ex_name}][{test_name}]:`
```api-blueprint
{error}
```
"""

SEPARATOR = "--------\n"
FINISHING_NOTE = "With 💙 from homework bot 🤖\n"

SUCCESS_TAG = "✔"
FAILED_TAG = "✘"


class MdWriter:
    """Write given tests results into a markdown file."""

    def __init__(self):
        """Initialize the writer."""
        self._md_table = TABLE_TEMPLATE.format(hw_name='Homework Name',
                                               ex_name='Exercise Name',
                                               test_name='Test Name',
                                               result_sign='Result')
        self._md_table += TABLE_SEPARATOR
        self._errors = ''  # Markdown part with errors.

    def update(self, hw_results):
        """Update the table of completion."""
        for hw_name, hw_dict in sorted(hw_results.items()):
            need_hw_name = True
            for ex_name, ex_dict in sorted(hw_dict.items()):
                need_ex_name = True
                for test_name, test_result in sorted(ex_dict.items()):
                    result_sign = SUCCESS_TAG \
                        if test_result.succeeded() \
                        else FAILED_TAG
                    self._md_table += TABLE_TEMPLATE.format(
                        hw_name=hw_name if need_hw_name else '',
                        ex_name=ex_name if need_ex_name else '',
                        test_name=test_name,
                        result_sign=result_sign)
                    self._add_error(hw_name, ex_name, test_name, test_result)
                    need_hw_name = False  # We only print homework name once.
                    need_ex_name = False  # We only print exercise name once.

    def write_md_file(self, md_file_path):
        """Write all the added content to the md file."""
        md_file_content = '# Test results\n'
        md_file_content += self._md_table
        if self._errors:
            md_file_content += '\n## Encountered errors\n'
            md_file_content += self._errors
        md_file_content += SEPARATOR
        md_file_content += FINISHING_NOTE
        with open(md_file_path, 'w') as md_file:
            md_file.write(md_file_content)

    def _add_error(self, hw_name, exercise_name, test_name, test_result):
        """Add a section of errors to the md file."""
        if test_result.succeeded():
            return
        self._errors += ERROR_TEMPLATE.format(hw_name=hw_name,
                                              ex_name=exercise_name,
                                              test_name=test_name,
                                              error=test_result.stderr)
