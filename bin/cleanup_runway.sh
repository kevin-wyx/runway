#!/bin/bash

set -e

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPTDIR/..
eval RUNWAYDIR=`pwd`
WORKSPACES_PATH=$RUNWAYDIR/guest_workspaces

echo
echo "                                                _____  "
echo "*******************************************    /     \ "
echo "*                                         *   | () () |"
echo "*     WARNING! Your work can be lost!     *    \  ^  / "
echo "*                                         *     |||||  "
echo "*******************************************     |||||  "
echo
echo "Running this script will delete everything under '${WORKSPACES_PATH}',"
echo "and will destroy your Vagrant VM along with all the containers it hosts."
echo
echo "All your uncommitted work in Runway WILL BE LOST. FOREVER."
echo
read -p "Are you sure you want to continue? [y/N] " -r
# If want the user to hit 'return' key, replace previous line with next one:
#read -p "your Vagrant VM. Are you sure you want to continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborting cleanup"
    exit 0
fi

cd $SCRIPTDIR
vagrant destroy --force
cd $WORKSPACES_PATH
ls | grep -v README | xargs rm -rf
