#!/bin/bash

# run external to the runway host

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OPTIONALRUNWAYCNAME=1
source $SCRIPTDIR/lib/get_container_connection_options.sh

ssh ${VAGRANTOPTIONS} ${RUNWAYHOST} lxc list && echo "Done"
