"""Write test results into a markdown file."""


TABLE_TEMPLATE = "| {ex_name} | {test_name} | {result_sign} |\n"
TABLE_SEPARATOR = "|---|---|:---:|\n"

ERROR_TEMPLATE = """- Exercise: `"{ex_name}"`, test: `"{test_name}"`:
```
{error}
```
"""

SUCCESS_TAG = "✔"
FAILED_TAG = "✘"


class MdWriter:
    """Write given tests results into a markdown file."""

    def __init__(self):
        """Initialize the writer."""
        self._md_table = TABLE_TEMPLATE.format(ex_name='Exercise Name',
                                               test_name='Test Name',
                                               result_sign='Result')
        self._md_table += TABLE_SEPARATOR
        self._errors = ''  # Markdown part with errors.

    def update(self, exercise_results):
        """Update the table of completion."""
        for ex_name, result_dict in sorted(exercise_results.items()):
            need_ex_name = True
            for test_name, result in sorted(result_dict.items()):
                result_sign = SUCCESS_TAG if result.succeeded() else FAILED_TAG
                self._md_table += TABLE_TEMPLATE.format(
                    ex_name=ex_name if need_ex_name else '',
                    test_name=test_name,
                    result_sign=result_sign)
                self._add_error(ex_name, test_name, result)
                need_ex_name = False  # We only print exercise name once.

    def write_md_file(self, md_file_path):
        """Write all the added content to the md file."""
        md_file_content = '# Test results\n'
        md_file_content += self._md_table
        if self._errors:
            md_file_content += '\n## Encountered errors\n'
            md_file_content += self._errors
        md_file_content += '--------\n'
        md_file_content += 'With 💙 from homework bot 🤖\n'
        with open(md_file_path, 'w') as md_file:
            md_file.write(md_file_content)

    def _add_error(self, exercise_name, test_name, test_result):
        """Add a section of errors to the md file."""
        if test_result.succeeded():
            return
        self._errors += ERROR_TEMPLATE.format(ex_name=exercise_name,
                                              test_name=test_name,
                                              error=test_result.error)
