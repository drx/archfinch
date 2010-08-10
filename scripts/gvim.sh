#!/bin/bash
#
# Open all project files.
#
gvim -p `find . -regextype posix-extended -regex ".*\.(py)" ! -regex ".*(__init__|manage|settings|tests.py).*" | sort`
gvim -p `find ./templates -regextype posix-extended -regex ".*\.html" | sort`
