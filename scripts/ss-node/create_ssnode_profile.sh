#!/bin/bash

PROFILE_PATH=$1
CONTAINER=$2


# check ss-node profile if lxc list doesn't have then create ss-node profile from template
echo "[i] Checking for existing container profile..."
echo
if [[ $(lxc profile list | grep $CONTAINER) ]]; then
  echo "[i] Profile '$CONTAINER' already exists. Cleaning up..."
  lxc profile delete $CONTAINER
  echo
fi

# generate container-specific LXC profile file
echo "[i] Generating LXD profile file for container..."
echo
cat $PROFILE_PATH/head.tmpl $PROFILE_PATH/devices.tmpl > /tmp/$CONTAINER.yml

# get all created ZFS volumes and add to LXC profile file
echo "[i] Updating LXD profile file with created 'disks'..."
echo
for zvol in {1..8}; do
  ZFS_VOLUME=$(ls -la /dev/zvol/$CONTAINER/ | sed "s@.*/@@" | grep zd | sed "s/zd//" | awk "NR==$zvol")
  #echo "Volume $zvol: $ZFS_VOLUME"
  cat <<EOT >> /tmp/$CONTAINER.yml
  disk$ZFS_VOLUME:
    major: "230"
    minor: "$ZFS_VOLUME"
    path: /dev/zd$ZFS_VOLUME
    type: unix-block
EOT
done

# set profile name in profile file before reading it in
sed -i "s/\[profile\]/$CONTAINER/" /tmp/$CONTAINER.yml

# create LXC profile and read in generated profile file into profile
echo "[i] Adding container profile to LXC..."
echo
lxc profile create $CONTAINER
cat /tmp/$CONTAINER.yml | lxc profile edit $CONTAINER

echo "[i] Cleaning up /tmp/$CONTAINER.yaml profile template"
rm -rf /tmp/$CONTAINER.yml

