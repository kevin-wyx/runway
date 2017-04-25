#!/bin/bash

set -e

CNAME=$1
if [ -z "$CNAME" ]; then
  echo "usage: $0 <container-name> [BASEIMAGE name] [--debug]"
  exit 1
fi
shift

BASEIMAGE=$1
if [ -z "$BASEIMAGE" ]; then
  BASEIMAGE=runway-base
fi

DEBUG=''
# if --debug is given in the list of arguments
if [[ " $* " =~ " --debug " ]]; then
    set -x
    DEBUG="--debug"
fi

lxc stop $CNAME
lxc publish $CNAME --alias $BASEIMAGE description="Created by swift runway"
lxc start $CNAME
