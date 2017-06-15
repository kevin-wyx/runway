#!/bin/bash

set -e

if [ `id -u` -ne 0 ]; then
    echo 'Must be run as root'
    exit 1
fi

# Directory containing the script, so that we can call other scripts
#DIR="$(dirname "$(readlink -f "${0}")")" # not supported on OSX
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

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

if [ -z ${4+x} ]; then
    VOLSIZE=10G
else
    VOLSIZE=$4
fi

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

$DIR/make_base_container.sh $DISTRO $CNAME $BASEIMAGE $VOLSIZE $DEBUG

INSTALLMODE=$(if [[ " $* " =~ " --no-install " ]]; then echo "--no-install"; fi)
$DIR/setup_and_run_ansible_on_guest.sh $CNAME $DEBUG $INSTALLMODE

# if we're in a "no install" mode, skip the rest
# we assume it's already all set up (ie started from a snapshot)
if [[ " $* " != *"--no-install"* ]]; then
    # Now find code repos in the guest and install them.
    # At this point, all the code is on the guest in `/home/swift/code/`.
    # We need to find repos there (excluding stuff like swift itself) and
    # call the install.sh command (not finding it is ok).
    #probably write this in python so it's a lot easier to parse? copy the py code to the container and run it there
    $DIR/generic_installer.py $CNAME $DEBUG


    DELETE_CONTAINER=''
    if [[ " $* " =~ " --delete-container " ]]; then
        DELETE_CONTAINER='--delete-container'
    fi

    if [[ ! " $* " =~ " --no-snapshot " ]]; then
        $DIR/snapshot_created_container.sh $CNAME $BASEIMAGE $DEBUG $DELETE_CONTAINER
    fi
fi
