#!/usr/bin/env python3

# do lxc list --format=json swift-runway
# ...and delete them


# while it would be cool if this worked, it doesn't and the docs are bad
# https://linuxcontainers.org/lxc/documentation/#python
# import lxc
# for defined in (True, False):
#     for active in (True, False):
#         x = lxc.list_containers(active=active, defined=defined)
#         print(x, '=> lxc.list_containers(active=%s, defined=%s)' % (active, defined))


import json
import subprocess
import shlex
import os


VOLUME_GROUP = 'swift-runway-vg01'

list_command = 'lxc list --format=json'
p = subprocess.run(shlex.split(list_command), stdout=subprocess.PIPE)

containers = json.loads(p.stdout.decode())
to_delete = [x['name'] for x in containers if x['name'].startswith('swift-runway-')]

if to_delete:
    delete_command = 'lxc delete --force %s' % ' '.join(to_delete)
    p = subprocess.run(shlex.split(delete_command))
    print('%d containers deleted' % len(to_delete))
else:
    print('No containers to delete')

# delete associated lvm volumes
try:
    lvlist = os.listdir('/dev/%s' % VOLUME_GROUP)
except FileNotFoundError:
    print('No volumes to delete')
else:
    for logical_volume in lvlist:
        delete_command = 'lvremove --yes /dev/%s/%s' % (VOLUME_GROUP, logical_volume)
        p = subprocess.run(shlex.split(delete_command), stdout=subprocess.PIPE)
    else:
        print('%d volumes deleted' % len(lvlist))
