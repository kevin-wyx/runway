#!/bin/bash

set -e

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPTDIR/..
eval RUNWAYDIR=`pwd`

echo
echo "Running this script will delete everything under '${RUNWAYDIR}/components'"
echo "and everything under '${RUNWAYDIR}/guest_workspaces', and will destroy"
read -p "your Vagrant VM. Are you sure you want to continue? [y/N] " -r
# If want the user to hit 'return' key, replace previous line with next one:
#read -p "your Vagrant VM. Are you sure you want to continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborting cleanup"
    exit 0
fi

cd $SCRIPTDIR
vagrant destroy --force
cd $RUNWAYDIR/guest_workspaces
ls | grep -v README | xargs rm -rf
