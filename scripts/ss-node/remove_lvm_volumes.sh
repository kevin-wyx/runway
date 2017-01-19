#!/bin/bash

DISK_SIZE=$1
# remove Volume Group name dm
sudo vgremove dm
# remove Physical Volume /dev/loop0
sudo pvremove /dev/loop0
# setup a loop device
sudo losetup -d /dev/loop0
# remove sparse disk file
sudo rm -rf /opt/swift-node-$DISK_SIZE.disk
