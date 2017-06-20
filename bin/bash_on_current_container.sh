#!/bin/bash

# run external to the runway host

if [ -z "$RUNWAYHOST" ]; then
    if vagrant ssh-config >/dev/null 2>&1; then
        echo "Connecting to Vagrant VM..."
        # We currently don't support multiple Vagrant hosts, but if we want to (some day), we just need to populate
        # this variable:
        VAGRANTHOST=""
        VAGRANTOPTIONS=`vagrant ssh-config $VAGRANTHOST | sed '/^[[:space:]]*$/d' |  awk 'NR>1 {print " -o "$1"="$2}'`
        RUNWAYHOST=localhost
    else
        RUNWAYHOST=dev
    fi
fi

if [ -z "$VAGRANTOPTIONS" ]; then
    echo "Connecting to $RUNWAYHOST..."
fi

if [ -z "$RUNWAYCNAME" ]; then
    RUNWAYCNAME="CURRENT"
fi

if [ $RUNWAYCNAME == "CURRENT" ]; then
    # get the last container in the list
    RUNWAYCNAME=`ssh ${VAGRANTOPTIONS} ${RUNWAYHOST} lxc list | grep swift-runway | cut -d '|' -f2 | awk '{$1=$1;print}' | tail -1`
fi

if [ -z $RUNWAYCNAME ]; then
    # no currently running containers
    echo "No runway guest containers found. Exiting."
    exit 1
fi

ssh -t ${VAGRANTOPTIONS} ${RUNWAYHOST} lxc exec ${RUNWAYCNAME} -- 'sudo su - swift'
