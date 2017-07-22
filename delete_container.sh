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
lvremove --yes /dev/swift-runway-vg01/$CNAME-vol0
lvremove --yes /dev/swift-runway-vg01/$CNAME-vol1
lvremove --yes /dev/swift-runway-vg01/$CNAME-vol2
lvremove --yes /dev/swift-runway-vg01/$CNAME-vol3
lvremove --yes /dev/swift-runway-vg01/$CNAME-vol4
lvremove --yes /dev/swift-runway-vg01/$CNAME-vol5
lvremove --yes /dev/swift-runway-vg01/$CNAME-vol6
lvremove --yes /dev/swift-runway-vg01/$CNAME-vol7
