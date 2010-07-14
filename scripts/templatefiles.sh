#!/bin/bash
#
# List all template files.
#
# Useful for opening the project in an editor like Vim which doesn't have
#  any functionality for projects. 
#
# You might use it like this:
#
#  vim -p `./templatefiles.sh`
find ./templates -regextype posix-extended -regex ".*\.html" | sort
