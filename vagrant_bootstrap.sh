#!/bin/bash

pvcreate /dev/sdc -y
vgcreate swift-runway-vg01 /dev/sdc -y
