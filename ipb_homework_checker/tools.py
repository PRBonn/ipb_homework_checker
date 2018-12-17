"""Handle various utility tasks."""
from os import path
from os import makedirs
from os import environ
import tempfile
import subprocess
import logging
import datetime

from .schema_tags import OutputTags

PKG_NAME = "ipb_homework_checker"
PROJECT_ROOT_FOLDER = path.abspath(path.dirname(path.dirname(__file__)))
DATE_PATTERN = "%Y-%m-%d %H:%M:%S"
MAX_DATE_STR = datetime.datetime.max.strftime(DATE_PATTERN)

EXPIRED_TAG = "expired"

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
    if not value:
        return None, "No value. Cannot convert to '{}'.".format(output_type)
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
        stdout = self.stdout
        if not stdout:
            stdout = ""
        if self.stderr:
            return "stdout: {}, stderr: {}".format(stdout.strip(),
                                                   self.stderr.strip())
        return stdout.strip()


def run_command(command, shell=True, cwd=path.curdir, env=environ, timeout=20):
    """Run a generic command in a subprocess.

    Args:
        command (str): command to run
    Returns:
        str: raw command output
    """
    try:
        startupinfo = None
        if shell and isinstance(command, list):
            command = subprocess.list2cmdline(command)
            log.debug("running command: \n%s", command)
        process = __run_subprocess(command,
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
        log.error("command '%s' finished with code: %s", e.cmd, e.returncode)
        log.debug("command output: \n%s", output_text)
        return CmdResult(returncode=e.returncode, stderr=output_text)
    except subprocess.TimeoutExpired as e:
        output_text = "Timeout: command '{}' ran longer than {} seconds".format(
            e.cmd.strip(), e.timeout)
        log.error(output_text)
        return CmdResult(returncode=1, stderr=output_text)


def __run_subprocess(*popenargs,
                     input=None,
                     timeout=None,
                     check=False,
                     **kwargs):
    """Run a command as a subprocess.

    Using the guide from StackOverflow:
    https://stackoverflow.com/a/36955420/1763680
    This command has been adapted from:
    https://github.com/python/cpython/blob/3.5/Lib/subprocess.py#L352-L399

    This code does essentially the same as subprocess.run(...) but makes sure to
    kill the whole process tree which allows to use the timeout even when using
    shell=True. The reason I don't want to stop using shell=True here is the
    convenience of piping arguments from one function to another.
    """
    if input is not None:
        if 'stdin' in kwargs:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = subprocess.PIPE
    import os
    import signal
    from subprocess import Popen, TimeoutExpired, CalledProcessError
    from subprocess import CompletedProcess
    with Popen(*popenargs, preexec_fn=os.setsid, **kwargs) as process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except TimeoutExpired:
            # Kill the whole group of processes.
            os.killpg(process.pid, signal.SIGINT)
            stdout, stderr = process.communicate()
            raise TimeoutExpired(process.args, timeout, output=stdout,
                                 stderr=stderr)
        retcode = process.poll()
        if check and retcode:
            raise CalledProcessError(retcode, process.args,
                                     output=stdout, stderr=stderr)
    return CompletedProcess(process.args, retcode, stdout, stderr)
