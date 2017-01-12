#!/bin/bash

set -e

CNAME=$1
if [ -z "$CNAME" ]; then
  echo "usage: $0 <container-name> [--debug]"
  exit 1
fi
shift

DEBUG=''
# if --debug is given in the list of arguments
if [[ " $* " =~ " --debug " ]]; then
    set -x
    DEBUG="--debug"
fi

# load the components
if [ ! -d ./components/swift/.git ]; then
    git clone https://github.com/openstack/swift.git ./components/swift
fi

# get all the guest-executed stuff pushed over
# lxc file push ./ansible/ $CNAME/root/
# unfortunately, lxc doesn't support directly pushing a whole directory
# https://github.com/lxc/lxd/issues/1218
tar cf - ./ansible | lxc exec $CNAME -- tar xf - -C /root/

# copy the components over
# lxc file push ./components/ $CNAME/root/
# unfortunately, lxc doesn't support directly pushing a whole directory
# https://github.com/lxc/lxd/issues/1218
tar cf - -C ./components . | lxc exec $CNAME -- tar xf - -C /root/

# install ansible
lxc exec $CNAME -- /bin/bash /root/ansible/install_ansible.sh $DEBUG

# run ansible playbook to bootstrap container
lxc exec $CNAME -- ansible-playbook -i "localhost," -c local /root/ansible/master_playbook.yaml
