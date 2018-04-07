# Homework checker #

This is a python module and script that can be used to check homeworks. One can
specify the expected results in the form of a `yaml` file specifying excercises
and specific tests for them. The result it a markdown file with a table of
results and a list of encountered errors.

## Prerequesits ##
We need `ruamel.yaml` and `schema` libraries to run this code. Install them
with:
```
sudo pip3 install ruamel.yaml schema
```
