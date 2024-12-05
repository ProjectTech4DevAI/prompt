#!/bin/bash

ROOT=`git rev-parse --show-toplevel`

_src=$ROOT/src/refine/summarize
python $_src/run.py --user-prompt $_src/user.txt
