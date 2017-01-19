#!/bin/bash
source ./vars/lxd-vars.sh

# container vars
CONTAINER="ubuntu-ss-node-template"
CONTROLLER="ssman"
CONTROLLER_IP="192.168.81.102"
DIST="ubuntu"
DIST_VERS="trusty"
DIST_ARCH="amd64"
HOSTNAME="$CONTAINER"
DOMAIN="swiftstack.dev"
FQDN="$HOSTNAME.$DOMAIN"
BUILD_DIR="/tmp"
BUILD_SCRIPT=""
DISK_SIZE=8800
PROFILE_PATH="./profiles/ssnode"

# set container name
#echo
#read -e -p ">>> Container name: " CONTAINER_NAME
#echo

#if [ $CONTAINER != $CONTAINER_NAME ]; then
#  CONTAINER="$CONTAINER_NAME"
#fi

CONTAINER=$1

echo $CONTAINER

# generate container-specific  zfs drives 
./scripts/ss-node/create_ssnode_zfs_drives.sh $CONTAINER $DISK_SIZE

# generate container-specific LXC profile file
./scripts/ss-node/create_ssnode_profile.sh $PROFILE_PATH $CONTAINER

echo "[i] creating drive layout into /tmp/drives.json..."
#remove temp drive json file
rm -rf /tmp/drives.json

#generate temp drive json file
echo "[" >> /tmp/drives.json && for zvol in {1..8}; do ZFS_VOLUME=$(ls -la /dev/zvol/$CONTAINER/ | sed "s@.*/@@" | grep zd | awk "NR==$zvol") && if [ $zvol != 8 ]; then echo { \"drive\": \"$ZFS_VOLUME\", \"mp\": \"/srv/$(($(($zvol % 4))+1))/node/d$zvol\" }, >> /tmp/drives.json ; else echo { \"drive\": \"$ZFS_VOLUME\", \"mp\": \"/srv/$(($(($zvol % 4))+1))/node/d$zvol\" } >> /tmp/drives.json;fi; done && echo "]" >> /tmp/drives.json

# double chck temp drive json file
echo "[i] display drive layout /tmp/drives.json"
cat /tmp/drives.json

# create new container
echo
echo "[i] Launching new container..."
echo
lxc launch ubuntu:16.04 $CONTAINER -p $CONTAINER
#lxc launch images:$DIST/$DIST_VERS/$DIST_ARCH $CONTAINER -p $CONTAINER
sleep 3

# check if running in virtual machine
if [[ $(sudo virt-what | grep virtualbox) == "virtualbox" ]]; then
  printf "\n[i] Running in a VirtualBox environment.\n\n"
  # update interfaces config if running in VM dev env
  $LXCFPUSH --uid="0" --gid="0" --mode="0644" ./templates/os/$DIST/network-interfaces-eth1.vm $CONTAINER/etc/network/interfaces
  # up eth1 interface
  $LXCEXEC $CONTAINER -- ifup eth1
else   # [[ $(sudo virt-what | grep kvm) != "kvm" ]]; then
  printf "\n[i] Not running in virtual machine.\n"
fi

printf "\n[i] Waiting for network to get ready...\n"
sleep 5

# register IPv4 addresses
IPV4_ETH0=$($LXCEXEC $CONTAINER -- ip addr show eth0 | grep -Po 'inet \K[\d.]+')
IPV4_ETH1=$($LXCEXEC $CONTAINER -- ip addr show eth1 | grep -Po 'inet \K[\d.]+')
printf "
[i] eth0 IP is: $IPV4_ETH0
    eth1 IP is: $IPV4_ETH1

"

# push bashrc template file
$LXCFPUSH --uid="0" --gid="0" --mode="0644" ./templates/bashrc.tmpl $CONTAINER/root/.bashrc

# install basic packages
$LXCEXEC $CONTAINER -- apt update
$LXCEXEC $CONTAINER -- apt install -y wget curl

# copy temp drives json file to container
echo "[i] copy /tmp/drives.json to container"
$LXCFPUSH --uid="0" --gid="0" --mode="0755" /tmp/drives.json $CONTAINER/tmp/drives.json

