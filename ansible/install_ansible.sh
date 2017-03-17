#!/bin/bash

# if --debug is given in the list of arguments
if [[ " $* " =~ " --debug " ]]; then
    set -x
fi

set +e

echo "Waiting on networking..."
for i in {1..20}; do
    ping -c 1 archive.ubuntu.com
    if [ $? -ne 0 ]; then
        sleep 5
    else
        break
    fi
done
echo "Done!"

distro="RHEL"
installer=`type -P yum`

if [ -z "$installer" ]; then
  installer=`which apt-get`
  distro="Debian"
  # the update step is needed to make sure package sources are available
  $installer update
fi

if [ -z "$installer" ]; then
  echo "Unknown or unsupported distro"
  exit 1
fi

$installer install -y python-pip build-essential gcc libssl-dev python-dev libffi-dev


pip install ansible
