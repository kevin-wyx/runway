#!/bin/bash

set -e

pvcreate /dev/sdc -y
vgcreate swift-runway-vg01 /dev/sdc -y

# We need LXD version 2.14 or higher in order to pre-seed lxd init.
# Our xenial box comes with LXD 2.0.10, so we'll have to install the backport
# version.
# We could just do:
#     apt-get install lxd/xenial-backports -y
# But we would risk getting a version that breaks our current config.

## This works:
apt-get install lxd-client=2.14-0ubuntu3~16.04.1 lxd=2.14-0ubuntu3~16.04.1 -y
lxd init --auto
cat <<EOF | lxd init --preseed
networks:
- name: lxdbr0
  type: bridge
  config:
    ipv4.address: auto
    ipv6.address: auto
profiles:
- name: default
  devices:
    eth0:
      name: eth0
      nictype: bridged
      parent: lxdbr0
      type: nic
    root:
      path: /
      pool: default
      type: disk
EOF
## End of what works

## This also seems to work:
#apt-get install lxd-client=2.14-0ubuntu3~16.04.1 lxd=2.14-0ubuntu3~16.04.1 -y
#dpkg-reconfigure debconf -f noninteractive -p medium lxd
#lxd init --auto
#lxc network create lxdbr0
#lxc network attach-profile lxdbr0 default eth0
## End of what also seems to work

/vagrant/start.sh RHEL runway-base swift-runway-`date +%F-%H-%M-%S-%N` 1G
su ubuntu
lxc list
