# Homework checker #

This is a python module and script that can be used to check homeworks.


## How to use it ##
One can specify the expected results in the form of a `yaml` file specifying
excercises and specific tests for them, then this file is fed into the
[`check_homework.py`](ipb_homework_checker/check_homework.py) script. The
result is a markdown file with a table of results and a list of encountered
errors.

To set up a new job script, follow the [`schema.yml`](schema/schema.yml) file.
The schema file is automatically generated whenever you run the tests of this
project, and your script should follow the guides defined in that schema file.
For an example job script, see an example from the tests of this project:
[`example_job.yml`](ipb_homework_checker/tests/data/homework/example_job.yml).

If you want to see a project that uses this checker, feel free to poke around
[homework-solutions-repo][solutions] project. If you have no access, ask me or
Cyrill for it.

## Prerequesits ##
We need `ruamel.yaml` and `schema` libraries to run this code. Install them
with:
```
sudo pip3 install ruamel.yaml schema
```

## Start digging ##
If you want to change anything, start from
[`check_homework.py`](ipb_homework_checker/check_homework.py) script and
dig from there.

[solutions]: https://gitlab.igg.uni-bonn.de/teaching/homework-solutions-repo
