"""Handle various subprocess-related tasks."""
from os import path
from os import makedirs
from os import environ
import tempfile
import subprocess
import logging

PKG_NAME = "homework_checker"

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
        output_text = ''.join(map(chr, output))
    except subprocess.CalledProcessError as e:
        output_text = e.output.decode("utf-8")
        log.debug("command finished with code: %s", e.returncode)
        log.debug("command output: \n%s", output_text)
    return output_text
