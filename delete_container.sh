# This script deletes a single container together with its profile and all its
# volumes without deleting its workspace.
#
# Please note this script doesn't delete any images.

#!/bin/bash

if [ `id -u` -ne 0 ]; then
    echo 'Must be run as root'
    exit 1
fi

CNAME=$1
if [ -z "$CNAME" ];  then
    echo "Required container name variable is not specified"
    echo
    echo "usage: $0 <CONTAINER-NAME>"
    exit 1
fi

set -e
set -x

lxc delete $CNAME --force
lxc profile delete $CNAME-profile
lvremove --yes /dev/swift-runway-vg01/$CNAME-vol*
