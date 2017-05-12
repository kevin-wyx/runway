#!/bin/bash

set -e

if [ `id -u` -ne 0 ]; then
    echo 'Must be run as root'
    exit 1
fi

# Directory containing the script, so that we can call other scripts
#DIR="$(dirname "$(readlink -f "${0}")")" # not supported on OSX
DIR="$( cd "$( dirname "${0}" )" && pwd )"

if [ -z ${1+x} ]; then
    DISTRO=ubuntu
else
    DISTRO=$1
fi

if [ -z ${2+x} ]; then
    BASEIMAGE=runway-base
else
    BASEIMAGE=$2
fi

if [ -z ${3+x} ]; then
    # Using colons makes using lxc-cli inconvenient, and using periods makes it
    # an invalid hostname, so just use all dashes
    TS=`date +%F-%H-%M-%S-%N`
    CNAME=swift-runway-$TS
else
    CNAME=$3
fi

echo $CNAME

# TODO: if we want to use --debug or --delete-container options
# but BASEIMAGE and/or CNAME are not specified, we will use
# the command options as the names for base image/container
# Same thing applies to snapshot_created_container.sh
DEBUG=''
# if --debug is given in the list of arguments
if [[ " $* " =~ " --debug " ]]; then
    set -x
    DEBUG="--debug"
fi

$DIR/make_base_container.sh $DISTRO $CNAME $BASEIMAGE $DEBUG

$DIR/setup_and_run_ansible_on_guest.sh $CNAME $DEBUG

#TODO: for anything in the components directory (other than some well-known stuff)
# look for the common install script and run it on the container

PROXYFS_INSTALLER=/home/swift/code/ProxyFS/src/github.com/swiftstack/ProxyFS/ci/ansible/install_proxyfs_runway.sh
# TODO: Uncomment this code to install ProxyFS
#if lxc exec $CNAME -- ls $PROXYFS_INSTALLER; then
    #lxc exec $CNAME -- $PROXYFS_INSTALLER
#fi

DELETE_CONTAINER=''
if [[ " $* " =~ " --delete-container " ]]; then
    DELETE_CONTAINER='--delete-container'
fi

if [[ ! " $* " =~ " --no-snapshot " ]]; then
    $DIR/snapshot_created_container.sh $CNAME $BASEIMAGE $DEBUG $DELETE_CONTAINER
fi
