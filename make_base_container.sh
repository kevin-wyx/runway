#!/bin/bash

set -e

# if --debug is given in the list of arguments
if [[ " $* " =~ " --debug " ]]; then
    set -x
fi

DISTRO=$1
if [ -z "$DISTRO" ];  then
    echo "Required DISTRO variable is not specified"
    echo
    echo "usage: $0 [--debug] DISTRO CNAME"
    exit 1
fi

if [ -z $2 ]; then
    echo "Required CNAME variable is not specified"
    echo
    echo "usage: $0 [--debug] DISTRO CNAME"
    exit 1
else
    CNAME=$2
fi

BASE=ubuntu:16.04
#if [ "$DISTRO" == "RHEL" ]; then
#    BASE=ci-base-image-centos
#fi



# NEW PLAN
# assume well-known lvm volume group on host
#   ...later we'll figure out how to make this
# ask lvm for devices from this vg
# map those devices to the lxc profile

#sudo vgcreate swift-runway-vg01 /dev/sda1 /dev/sdb1 /dev/sdc1 /dev/sdd1

VG_NAME=swift-runway-vg01

# 4 servers, 2 drives each == 8 drives. make them 10GB each
# TODO: make persistent (-My) and set --minor? if not, what about reboots of host?
for i in {0..7}; do
    lvcreate --size 10G --name $CNAME-vol$i $VG_NAME >/dev/null
    MINOR=`sudo lvdisplay /dev/$VG_NAME/$CNAME-vol$i | grep "Block device" | awk '{print $3}' | cut -d':' -f2`
    echo $MINOR
done

# now get the mejor and minor versions for each of these and put them into the lxc profile

exit 1


# create a large(-ish) file to be used for storage in the guest
mkdir -p /opt/runway_volumes/
# 10GB per drive, 4 servers in a SAIO, 2 drives each = 80GB
# I'm creating an 81GiB file here just to give a little headroom
truncate -s 81G /opt/runway_volumes/$CNAME.volume_file

# carve up the file into 8 block devices with lvm

eval "$(date +'today=%F now=%s')"
midnight=$(date -d "$today 0" +%s)
TODAYS_SECONDS="$((now - midnight))"

#mount it as loopback?
# why does this work without mounting it? does /dev/loop0 need to be there?
SECTORS=20971520  # 10GB / 512b sectors
for i in {0..7}; do
    # dmsetup create $CNAME-0 --table "0 $SECTORS linear /dev/loop0 0"
    # dmsetup create $CNAME-1 --table "0 $SECTORS linear /dev/loop0 $SECTORS"
    # is 252 for major number always correct?
    MINOR=$((i+TODAYS_SECONDS))
    DEV_NAME=$CNAME-$i
    dmsetup create --major 252 --minor $MINOR $DEV_NAME --notable 
    echo "dev made"
    TABLE="0 $SECTORS linear /dev/loop0 $((SECTORS*i))"
    echo $TABLE
    dmsetup load $DEV_NAME --table "$TABLE"
done
# dmsetup create $CNAME-N --table "0 $SECTORS linear /dev/loop0 $SECTORS*N"

MINOR=`dmsetup ls | grep $CNAME | cut -d: -f2 | cut -d')' -f1`
MAJOR=252

for n in $MINOR; do
    echo $n
done
exit 1

# cleanup
#sudo dmsetup ls | grep swift-runway-test | awk '{print $1}' | xargs sudo dmsetup remove

# make a container profile that maps those 8 block devices to the guest
lxc profile create $CNAME-profile
cat container-base/swift-runway-v1.yaml | lxc profile edit $CNAME-profile

# launch the new container
# lxc launch $BASE $CNAME -p swift-runway-v1
lxc launch $BASE $CNAME -p ci
