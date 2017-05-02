#!/bin/bash


SRC=$1
DESTCNAME=$2

#TODO: handle special cases of DESTCNAME (NEW and CURRENT)
#TODO: handle errors when the CNAME doesn't exist (check if DESTDIR exists or not)

# rsync the src directory to the appropriate workspace for the given container
DESTDIR=~/runway/guest_workspaces/${DESTCNAME}_shared_code/

#TODO: maybe add in the necessary excludes?
rsync -a --delete $SRC $DESTDIR

#TODO: start/restart processes in the container? probably not
