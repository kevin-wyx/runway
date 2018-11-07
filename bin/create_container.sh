#!/bin/bash

# run external to the runway host

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPTDIR/lib/get_container_connection_options.sh

# Ideally we should get expected options from the manifest
# But for now, you must specify -d <DISTRO> -v <VOLSIZE> e.g., -d RHEL -v 1G
ssh ${VAGRANTOPTIONS} ${RUNWAYHOST} RUNWAYCNAME=${RUNWAYCNAME} sudo /vagrant/start.py ${*} && echo "Done"
