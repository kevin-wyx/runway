#!/bin/bash

if [ -z ${1+x} ]; then
    DISTRO=ubuntu
else
    DISTRO=$1
fi

DEBUG=''
# if --debug is given in the list of arguments
if [[ " $* " =~ " --debug " ]]; then
    set -x
    DEBUG="--debug"
fi

# Using colons makes using lxc-cli inconvenient, and using periods makes it
# an invalid hostname, so just use all dashes
TS=`date +%F-%H-%M-%S-%N`
CNAME=swift-runway-$TS

echo $CNAME

./make_base_container.sh $DISTRO $CNAME $DEBUG

./setup_and_run_ansible_on_guest.sh $CNAME $DEBUG
