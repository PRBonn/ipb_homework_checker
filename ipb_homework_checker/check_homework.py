#!/usr/bin/python3
"""Script to check this homework."""
import argparse
import logging

from .checker import Checker
from .md_writer import MdWriter


logging.basicConfig()
log = logging.getLogger("GHC")
log.setLevel(logging.INFO)


def main():
    """Run this script."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose',
        help='Make the output verbose.',
        action='store_true')
    parser.add_argument(
        '-i', '--input',
        help='An input *.yml file with the job definition.',
        required=True)
    parser.add_argument(
        '-o', '--output',
        help='An output *.md file with the results.',
        required=True)
    args = parser.parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)
        log.debug('Enable DEBUG logging.')
    # Read the job file.
    log.debug('Reading from file "%s"', args.input)
    checker = Checker(args.input)
    results = checker.check_homework()
    md_writer = MdWriter()
    md_writer.update(results)
    # Write the resulting markdown file.
    log.debug('Writing to file "%s"', args.output)
    md_writer.write_md_file(args.output)


if __name__ == "__main__":
    main()
