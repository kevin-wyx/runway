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
import sys
import shutil


if os.geteuid() != 0:
    print('must be run as root')
    sys.exit(1)

delete_everything = '--all' in sys.argv[1:]

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

# delete associated lxc profiles
profile_list_command = 'lxc profile list'
p = subprocess.run(shlex.split(profile_list_command), stdout=subprocess.PIPE)
profiles = p.stdout.decode().split('\n')
to_delete = [x for x in profiles if x.startswith('swift-runway-')]
if to_delete:
    for profile in to_delete:
        delete_command = 'lxc profile delete %s' % profile
        p = subprocess.run(shlex.split(delete_command))
    print('%d profles deleted' % len(to_delete))
else:
    print('No profles to delete')

# delete container working spaces
for dirname in os.listdir('guest_workspaces'):
    if dirname == 'README':
        continue
    dirname = 'guest_workspaces/' + dirname
    shutil.rmtree(dirname)

# delete snapshotted container images
images_to_delete = []
image_list_command = 'lxc image list description="Created by swift runway"'
p = subprocess.run(shlex.split(image_list_command), stdout=subprocess.PIPE)
for line in p.stdout.decode().split('\n'):
    if "Created by swift runway" in line:
        parts = line.split('|')
        fingerprint = parts[2].strip()
        if delete_everything or 'runway-base' not in line:
            images_to_delete.append(fingerprint)
if images_to_delete:
    print('Deleting %d images' % len(images_to_delete))
    image_delete_command = 'lxc image delete %s' % ' '.join(images_to_delete)
    p = subprocess.run(shlex.split(image_delete_command))
else:
    print('No images to delete')
