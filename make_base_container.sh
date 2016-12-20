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
    echo "usage: $0 [--debug] DISTRO CNAME"
    exit 1
fi

if [ -z $2 ]; then
    echo "Required CNAME variable is not specified"
    echo
    echo "usage: $0 [--debug] DISTRO CNAME"
    exit 1
else
    CNAME=$2
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

# launch the new container
lxc launch $BASE $CNAME -p swift-runway-v1
