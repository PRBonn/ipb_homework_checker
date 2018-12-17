"""Write test results into a markdown file."""

from .tools import EXPIRED_TAG

TABLE_TEMPLATE = "| {hw_name} | {task_name} | {test_name} | {result_sign} |\n"
TABLE_SEPARATOR = "|---|---|---|:---:|\n"

ERROR_TEMPLATE = """### `[{hw_name}][{task_name}][{test_name}]:`

*stderr*:
```apiblueprint
{stderr}
```
*stdout*:
```
{stdout}
```
--------
"""

EXPIRED_TEMPLATE = """

### `[{hw_name}][Past Deadline][Errors Hidden]`

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
                                               task_name='Task Name',
                                               test_name='Test Name',
                                               result_sign='Result')
        self._md_table += TABLE_SEPARATOR
        self._errors = ''  # Markdown part with errors.

    def update(self, hw_results):
        """Update the table of completion."""
        for hw_name, hw_dict in sorted(hw_results.items()):
            need_hw_name = True
            expired = False
            if EXPIRED_TAG in hw_dict:
                expired = True
            for task_name, ex_dict in sorted(hw_dict.items()):
                if task_name == EXPIRED_TAG:
                    # Maybe there is a better way to handle this, but I don't
                    # want to dig into this right now. We have added the
                    # EXPIRED_TAG to this dict and need to ignore it here.
                    continue
                need_task_name = True
                for test_name, test_result in sorted(ex_dict.items()):
                    result_sign = SUCCESS_TAG \
                        if test_result.succeeded() \
                        else FAILED_TAG
                    extended_hw_name = hw_name + " `[PAST DEADLINE]`" \
                        if expired else hw_name
                    self._md_table += TABLE_TEMPLATE.format(
                        hw_name=extended_hw_name if need_hw_name else '',
                        task_name=task_name if need_task_name else '',
                        test_name=test_name,
                        result_sign=result_sign)
                    self._add_error(hw_name,
                                    task_name,
                                    test_name,
                                    test_result,
                                    expired)
                    need_hw_name = False  # We only print homework name once.
                    need_task_name = False  # We only print Task name once.

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

    def _add_error(self, hw_name, task_name, test_name, test_result, expired):
        """Add a section of errors to the md file."""
        if test_result.succeeded():
            return
        if expired:
            self._errors += EXPIRED_TEMPLATE.format(hw_name=hw_name)
            return
        self._errors += ERROR_TEMPLATE.format(hw_name=hw_name,
                                              task_name=task_name,
                                              test_name=test_name,
                                              stderr=test_result.stderr,
                                              stdout=test_result.stdout)
