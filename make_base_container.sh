#!/bin/bash

set -e

# if --debug is given in the list of arguments
if [[ " $* " =~ " --debug " ]]; then
    set -x
fi

DISTRO=$1
if [ -z "$DISTRO" ];  then
    echo "Required DISTRO variable is not specified"
    echo
    echo "usage: $0 [--debug] DISTRO"
    exit 1
fi

BASE=ubuntu:16.04
#if [ "$DISTRO" == "RHEL" ]; then
#    BASE=ci-base-image-centos
#fi

# add our profile, not an error if it already exists
set +e
lxc profile create swift-runway-v1 2>/dev/null
set -e
cat container-base/swift-runway-v1.yaml | lxc profile edit swift-runway-v1

# Using colons makes using lxc-cli inconvenient, and using periods makes it
# an invalid hostname, so just use all dashes
TS=`date +%F-%k-%M-%S-%N`
CNAME=swift-runway-$TS

# launch the new container
lxc launch $BASE $CNAME -p swift-runway-v1

echo $CNAME launched
