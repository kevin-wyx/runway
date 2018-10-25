#!/bin/bash

if [[ $# -gt 0 ]]; then
    RUNWAYCNAME="$1"
fi

# run external to the runway host

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPTDIR/lib/get_container_connection_options.sh

ssh -t ${VAGRANTOPTIONS} ${RUNWAYHOST} lxc exec ${RUNWAYCNAME} -- 'sudo su - swift'
