#!/bin/bash

CONTAINER=$1
DISK_SIZE=$2

sudo mkdir /opt/zfs/ -p

# create sparse file for zpool
echo "[i] Creating sparse file..."
echo
sudo mkdir -p /opt/zfs/$CONTAINER
sudo dd if=/dev/zero of=/opt/zfs/$CONTAINER/$CONTAINER.disk bs=1M count=$DISK_SIZE

# create zpool for to use for Swift disks
echo
echo "[i] Creating zpool on sparse file..."
echo
sudo zpool create $CONTAINER /opt/zfs/$CONTAINER/$CONTAINER.disk

# set up ZFS volumes for container
# as in: sudo zfs create -V 1G swift01/d0 ... and so on
echo "[i] Setting up ZFS volumes on zpool..."
echo
for disk in {0..7}; do
  sudo zfs create -V 1G $CONTAINER/d$disk
done
