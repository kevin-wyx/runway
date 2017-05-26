#!/bin/bash

# this runs on the host and is called by a remote machine, given the name of
# the code directory and the container to put it in

# Directory containing the script, so that we can call other scripts
#DIR="$(dirname "$(readlink -f "${0}")")" # not supported on OSX
DIR="$( cd "$( dirname "${0}" )" && pwd )"

#TODO: rewrite in python, because ... wow

SRC=$1
CNAME=$2

#TODO: add a "NEW" special name?

if [ $CNAME == "CURRENT" ]; then
    CNAME=`lxc list | grep swift-runway | cut -d '|' -f2 | awk '{$1=$1;print}' | tail -1`
fi

if [ -z $CNAME ]; then
    # no currently running containers
    exit 1
    # alternatively could put it in components and make a container
fi

#TODO: filter off "CURRENT_" prefix of $SRC

cd `dirname $SRC`
tar cf - `basename $SRC` | lxc exec $CNAME -- tar xf - -C /home/swift/code/
cd -


#TODO: a reinstall/restart flag to redo setup maybe? but how do we know how to do that?
