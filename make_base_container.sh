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
    echo "usage: $0 [--debug] DISTRO CNAME [BASEIMAGE] [VOLSIZE]"
    exit 1
fi

if [ -z $2 ]; then
    echo "Required CNAME variable is not specified"
    echo
    echo "usage: $0 [--debug] DISTRO CNAME [BASEIMAGE] [VOLSIZE]"
    exit 1
else
    CNAME=$2
fi

BASEIMAGE=ubuntu:16.04
if [ "$DISTRO" == "RHEL" ]; then
   BASEIMAGE=images:centos/7/amd64
fi
DEFAULTIMAGE=$BASEIMAGE
if [ -z $3 ]; then
    echo "Optional BASEIMAGE variable is not specified. Using $BASEIMAGE"
    echo
    echo "usage: $0 [--debug] DISTRO CNAME [BASEIMAGE] [VOLSIZE]"
else
    BASEIMAGE=$3
fi

if [ -z $4 ]; then
    VOLSIZE=10G
else
    VOLSIZE=$4
fi

# snapshot the components directory into a container-specific working dir
working_dir=$DIR/guest_workspaces/${CNAME}_shared_code/
mkdir -p $working_dir
rsync -a $DIR/components/ $working_dir

# assume well-known lvm volume group on host
#   ...later we'll figure out how to make this dynamic
VG_NAME=swift-runway-vg01

# make a container profile that maps 8 block devices to the guest
lxc profile create $CNAME-profile
$DIR/make_lxc_profile.py $CNAME $VG_NAME $VOLSIZE | lxc profile edit $CNAME-profile

# launch the new container
lxc launch $BASEIMAGE $CNAME -p $CNAME-profile || lxc launch $DEFAULTIMAGE $CNAME -p $CNAME-profile
