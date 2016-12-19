#!/bin/bash

distro="RHEL"
installer=`type -P yum`

if [ -z "$installer" ]; then
  installer=`which apt-get`
  distro="Debian"
fi

if [ -z "$installer" ]; then
  echo "Unknown or unsupported distro"
  exit 1
fi

if [ "$distro" == "RHEL" ]; then
  $installer install -y epel-release
fi

$installer install -y ansible
