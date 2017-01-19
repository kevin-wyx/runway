#!/bin/bash

DISK_SIZE=$1
echo "===createing test volume $DISK_SIZE==="

# install lvm
PKG_OK=$(sudo dpkg-query -l lvm2|grep lvm2)
if [ "" == "$PKG_OK" ]; then
  echo "install lvm now..."
  sudo apt install -y lvm2
else
  echo "checked lvm2 and found $PKG_OK"
fi

# create 5GB sparse disk file
sudo dd if=/dev/zero of=/opt/swift-node-$DISK_SIZE.disk bs=1M count=$DISK_SIZE

# setup a loop device
sudo losetup -f /opt/swift-node-$DISK_SIZE.disk

# list for double check
sudo losetup -a

# Add /dev/loop0 to the Physical Volume
sudo pvcreate /dev/loop0

# Create a Volume Group named dm containing /dev/loop0
sudo vgcreate -s 16M dm /dev/loop0

# Create Logical Volumes in dm (Volume Group)
for i in {0..4}; do echo "run lvcreate -L 1G -n $i dm" && sudo lvcreate -L 1G -n $i dm;done

# Final Check via lsblk
echo "===test volume $DISK_SIZE ready==="
sudo lsblk
