#!/bin/bash

set -e

pvcreate /dev/sdc -y
vgcreate swift-runway-vg01 /dev/sdc -y

apt-get update

lxd init --auto
usermod -G lxd vagrant
lxc list > /dev/null
sudo -H -u ubuntu bash -c 'lxc list > /dev/null'
sudo -H -u vagrant bash -c 'lxc list > /dev/null'
apt-get install linux-generic -y

if [ -z "$DISTRO" ]; then
    DISTRO=centos7.5
fi
/vagrant/start.py -d $DISTRO -v 1G --debug
