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

# get all the guest-executed stuff pushed over
# lxc file push ./ansible/ $CNAME/root/
# unfortunately, lxc doesn't support directly pushing a whole directory
# https://github.com/lxc/lxd/issues/1218
tar cf - ./ansible | lxc exec $CNAME -- tar xvf - -C /root/

# install ansible
lxc exec $CNAME -- /bin/bash /root/ansible/install_ansible.sh $DEBUG

# run ansible playbook to bootstrap container
lxc exec $CNAME -- ansible-playbook -i "localhost," -c local /root/ansible/master_playbook.yaml
