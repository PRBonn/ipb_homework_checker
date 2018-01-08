#!/usr/bin/python3
"""Script to check this homework."""
import sys

from checker import Checker
from md_writer import MdWriter


def main():
    """Run this script."""
    checker = Checker(sys.argv[1])
    results = checker.check_homework()
    md_writer = MdWriter()
    md_writer.update(results)
    md_writer.write_md_file('test.md')


if __name__ == "__main__":
    main()
