#!/bin/bash

# this runs on the host and is called by a remote machine, given the name of
# the code directory and the container to put it in

# Directory containing the script, so that we can call other scripts
#DIR="$(dirname "$(readlink -f "${0}")")" # not supported on OSX
DIR="$( cd "$( dirname "${0}" )" && pwd )"

#TODO: rewrite in python, because ... wow

SRC=$1
CNAME=$2

base=`basename $SRC`
base_no_prefix=`echo ${base} | sed "s/${CNAME}_//g"`

#TODO: add a "NEW" special name?

if [ $CNAME == "CURRENT" ]; then
    CNAME=`lxc list | grep swift-runway | cut -d '|' -f2 | awk '{$1=$1;print}' | tail -1`
fi

if [ -z $CNAME ]; then
    # no currently running containers
    exit 1
    # alternatively could put it in components and make a container
fi

cd `dirname $SRC`
tar cf - $base | lxc exec $CNAME -- tar xf - -C /home/swift/code/
lxc exec $CNAME -- mv /home/swift/code/${base} /home/swift/code/${base_no_prefix}
cd -


#TODO: a reinstall/restart flag to redo setup maybe? but how do we know how to do that?
