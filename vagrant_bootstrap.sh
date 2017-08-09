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
#
# On the other hand, using a specific version has proven to be wrong, as there
# is only one backport version, and it keeps changing. The way we used to do
# that was:
#     apt-get install lxd-client=2.15-0ubuntu6~ubuntu16.04.1 lxd=2.15-0ubuntu6~ubuntu16.04.1 -y
# And this is how we checked the currently available backports version:
#     apt-cache policy lxd

# So what we'll do is install whatever backport is available only if our
# current version is lower than 2.14
function version_gt() { test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"; }
current_lxd_version=`lxd --version`
if version_gt "2.14" $current_lxd_version; then
    apt-get update
    apt-get install lxd/xenial-backports -y
else
    echo "************************************"
    echo " Current LXD version is new enough!"
    echo " $current_lxd_version"
    echo "************************************"
fi

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

lxc list > /dev/null
sudo -H -u ubuntu bash -c 'lxc list > /dev/null'
/vagrant/start.py -d RHEL -v 1G
