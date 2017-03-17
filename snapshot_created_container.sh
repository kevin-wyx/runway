#!/bin/bash

set -e

CNAME=$1
if [ -z "$CNAME" ]; then
  echo "usage: $0 <container-name> [--debug]"
  exit 1
fi
shift

DEBUG=''
# if --debug is given in the list of arguments
if [[ " $* " =~ " --debug " ]]; then
    set -x
    DEBUG="--debug"
fi

lxc publish --force $CNAME --alias runway-base
