"""Handle various utility tasks."""
from os import path
from os import makedirs
from os import environ
import tempfile
import subprocess
import logging

PKG_NAME = "homework_checker"
ROOT_FOLDER = path.dirname(path.dirname(__file__))

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
    return path.join(ROOT_FOLDER, new_path)


class CmdResult:
    """A small container for command result."""

    def __init__(self, output=None, error=None):
        """Initialize either output of error."""
        self.output = output
        self.error = error

    def succeeded(self):
        """Check if the command succeeded."""
        return self.error is None


def run_command(command, shell=True, cwd=path.curdir, env=environ):
    """Run a generic command in a subprocess.

    Args:
        command (str): command to run
    Returns:
        str: raw command output
    """
    try:
        stdin = None
        startupinfo = None
        if isinstance(command, list):
            command = subprocess.list2cmdline(command)
            log.debug("running command: \n%s", command)
        output = subprocess.check_output(command,
                                         stdin=stdin,
                                         stderr=subprocess.STDOUT,
                                         shell=shell,
                                         cwd=cwd,
                                         env=env,
                                         startupinfo=startupinfo)
        return CmdResult(output=output.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        output_text = e.output.decode("utf-8")
        log.debug("command finished with code: %s", e.returncode)
        log.debug("command output: \n%s", output_text)
        return CmdResult(error=output_text)
