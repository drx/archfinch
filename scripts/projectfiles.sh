#!/bin/bash
#
# List all project .py files.
#
# Useful for opening the project in an editor like Vim which doesn't have
#  any functionality for projects. 
#
# You might use it like this:
#
#  vim -p `./projectfiles.sh`
find . -regextype posix-extended -regex ".*\.(py)" ! -regex ".*(__init__|manage|settings|tests.py).*" | sort
