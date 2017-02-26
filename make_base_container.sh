#!/bin/bash

set -e

# if --debug is given in the list of arguments
if [[ " $* " =~ " --debug " ]]; then
    set -x
fi

# Directory containing the script, so that we can call other scripts
#DIR="$(dirname "$(readlink -f "${0}")")" # not supported on OSX
DIR="$( cd "$( dirname "${0}" )" && pwd )"

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

# snapshot the components directory into a container-specific working dir
working_dir=guest_workspaces/${CNAME}_shared_code/
mkdir -p $working_dir
rsync -a components/ $working_dir

# assume well-known lvm volume group on host
#   ...later we'll figure out how to make this
VG_NAME=swift-runway-vg01

# make a container profile that maps 8 block devices to the guest
lxc profile create $CNAME-profile
$DIR/make_lxc_profile.py $CNAME $VG_NAME | lxc profile edit $CNAME-profile

# launch the new container
lxc launch $BASE $CNAME -p $CNAME-profile
