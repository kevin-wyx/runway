#!/bin/bash

# run external to the runway host

if [ -z "$RUNWAYHOST" ]; then
    RUNWAYHOST=dev
fi

if [ -z "$RUNWAYCNAME" ]; then
    RUNWAYCNAME="CURRENT"
fi

if [ $RUNWAYCNAME == "CURRENT" ]; then
    # get the last container in the list
    RUNWAYCNAME=`ssh ${RUNWAYHOST} lxc list | grep swift-runway | cut -d '|' -f2 | awk '{$1=$1;print}' | tail -1`
fi

if [ -z $RUNWAYCNAME ]; then
    # no currently running containers
    echo "No runway guest containers found. Exiting."
    exit 1
fi

ssh -t ${RUNWAYHOST} lxc exec ${RUNWAYCNAME} -- bash
