"""Handle various utility tasks."""
from os import path
from os import makedirs
from os import environ
import tempfile
import subprocess
import logging

from schema_tags import OutputTags

PKG_NAME = "homework_checker"
PROJECT_ROOT_FOLDER = path.abspath(path.dirname(path.dirname(__file__)))
log = logging.getLogger("GHC")


def get_temp_dir():
    """Create a temporary folder if needed and return it."""
    tempdir = path.join(tempfile.gettempdir(), PKG_NAME)
    if not path.exists(tempdir):
        makedirs(tempdir)
    return tempdir


def create_folder_if_needed(directory):
    """Create a folder if it does not exist."""
    if not path.exists(directory):
        makedirs(directory)


def expand_if_needed(input_path):
    """Expand the path if it is not absolute."""
    if path.isabs(input_path):
        return input_path
    new_path = path.expanduser(input_path)
    if path.isabs(new_path):
        # This path needed user expansion. Now that the user home directory is
        # expanded this is a full absolute path.
        return new_path
    # The user could not be expanded, so we assume it is just another relative
    # path to the project directory. Mostly used for testing purposes here.
    return path.join(PROJECT_ROOT_FOLDER, new_path)


def convert_to(output_type, value):
    """Convert the value to a specified type."""
    try:
        if output_type == OutputTags.STRING:
            result = str(value).strip()
        if output_type == OutputTags.NUMBER:
            result = float(value)
    except ValueError as e:
        log.error('Exception: %s.', e)
        return None, str(e)
    return result, "OK"


class CmdResult:
    """A small container for command result."""
    SUCCESS = 0
    FAILURE = 13

    def __init__(self, returncode=None, stdout=None, stderr=None):
        """Initialize either stdout of stderr."""
        self._returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    def succeeded(self):
        """Check if the command succeeded."""
        if self.returncode is not None:
            return self.returncode == CmdResult.SUCCESS
        if self.stderr:
            return False
        return True

    @property
    def returncode(self):
        """Get returncode."""
        return self._returncode

    @property
    def stdout(self):
        """Get stdout."""
        return self._stdout

    @property
    def stderr(self):
        """Get stderr."""
        return self._stderr

    @stderr.setter
    def stderr(self, value):
        self._returncode = None  # We can't rely on returncode anymore
        self._stderr = value

    @staticmethod
    def success():
        """Return a cmd result that is a success."""
        return CmdResult(stdout="Success!")

    def __repr__(self):
        """Representatin of command result."""
        if self.stderr:
            return "stdout: {}, stderr: {}".format(self.stdout.strip(),
                                                   self.stderr.strip())
        return self.stdout.strip()


def run_command(command, shell=True, cwd=path.curdir, env=environ, timeout=20):
    """Run a generic command in a subprocess.

    Args:
        command (str): command to run
    Returns:
        str: raw command output
    """
    try:
        startupinfo = None
        if isinstance(command, list):
            command = subprocess.list2cmdline(command)
            log.debug("running command: \n%s", command)
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=shell,
                                 cwd=cwd,
                                 env=env,
                                 startupinfo=startupinfo,
                                 timeout=timeout)
        return CmdResult(returncode=process.returncode,
                         stdout=process.stdout.decode('utf-8'),
                         stderr=process.stderr.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        output_text = e.output.decode("utf-8")
        log.debug("command finished with code: %s", e.returncode)
        log.debug("command output: \n%s", output_text)
        return CmdResult(returncode=e.returncode, stderr=output_text)
