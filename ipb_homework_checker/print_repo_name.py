#!/usr/bin/python3
"""A script to parse an input git url and get it's wiki counterpart.

Attributes:
    wiki_repo_mask (str): mask of wiki git repo
"""
import sys

from .tools import parse_git_url

wiki_repo_mask = "git@{domain}:{user}/{project}.wiki.git"
repo_mask = "git@{domain}:{user}/{project}.git"


def main():
    """Print the name of the repo."""
    if len(sys.argv) < 3:
        print("ERROR: must be supplied with a git url and type [wiki|code]")
        print("[Example]: {binary} {repo} {type}".format(
            binary='python3 print_repo_name.py',
            repo='git@gitlab.igg.uni-bonn.de:igor/some_project.git',
            type='wiki'))
        print("[Example]: {binary} {repo} {type}".format(
            binary='python3 print_repo_name.py',
            repo='https://gitlab.ipb.uni-bonn.de/igor/some_project.git',
            type='code'))
        exit(1)
    if len(sys.argv) == 3:
        repo = sys.argv[1]
        domain, user, project = parse_git_url(repo)
        repo_type = sys.argv[2]
        if repo_type == 'wiki':
            print(wiki_repo_mask.format(domain=domain,
                                        user=user,
                                        project=project))
        elif repo_type == 'code':
            print(repo_mask.format(domain=domain,
                                   user=user,
                                   project=project))
        else:
            print('ERROR: type "{}" is not "wiki" or "code"'.format(repo_type))


if __name__ == '__main__':
    main()
