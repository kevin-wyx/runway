#!/bin/bash

set -e

PLAYBOOK=master_playbook.yaml

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

# install ansible
lxc file push ./ansible/install_ansible.sh $CNAME/tmp/
lxc exec $CNAME -- /bin/bash /tmp/install_ansible.sh $DEBUG

# run ansible playbook to bootstrap container
#lxc file push ansible/$PLAYBOOK $CNAME/tmp/
#lxc exec $CNAME -- ansible-playbook -i "localhost," -c local /tmp/$PLAYBOOK
