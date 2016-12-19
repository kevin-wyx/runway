#!/bin/bash

set -e

PLAYBOOK=master_playbook.yaml

CNAME=$1
if [ -z "$CNAME" ]; then
  echo "usage: $0 <container-name>"
  exit 1
fi

# install ansible
lxc file push ./ansible/install-ansible.sh $CNAME/tmp/
lxc exec $CNAME -- /bin/bash /tmp/install-ansible.sh

# run ansible playbook to bootstrap container
lxc file push ansible/$PLAYBOOK $CNAME/tmp/
lxc exec $CNAME -- ansible-playbook -i "localhost," -c local /tmp/$PLAYBOOK
