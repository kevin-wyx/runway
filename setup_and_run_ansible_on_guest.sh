#!/bin/bash

set -e

# Directory containing the script, so that we can call other scripts
#DIR="$(dirname "$(readlink -f "${0}")")" # not supported on OSX
DIR="$( cd "$( dirname "${0}" )" && pwd )"

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

# check if we're in "no install" mode
if [[ " $* " != *"--no-install"* ]]; then
    # get all the guest-executed stuff pushed over
    # lxc file push ./ansible/ $CNAME/root/
    # unfortunately, lxc doesn't support directly pushing a whole directory
    # https://github.com/lxc/lxd/issues/1218
    cd $DIR && tar cf - ansible | lxc exec $CNAME -- tar xf - -C /root/ && cd -

    # install ansible
    lxc exec $CNAME -- /bin/bash /root/ansible/install_ansible.sh $DEBUG
    EXTRA_VARS="-e no_install=false"
else
    EXTRA_VARS="-e no_install=true"
fi

# run the bootstrap playbook
lxc exec $CNAME -- ansible-playbook -i "localhost," -c local $EXTRA_VARS /root/ansible/bootstrap.yaml

# check if we're in "no install" mode
if [[ " $* " != *"--no-install"* ]]; then
    # run ansible playbook to bootstrap container
    lxc exec $CNAME -- ansible-playbook -i "localhost," -c local /root/ansible/master_playbook.yaml
fi
