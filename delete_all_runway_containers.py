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


import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys


def parse_profiles_list(cli_output):
    profiles = []
    lines = cli_output.split('\n')
    for line in lines:
        result = re.match('(^\|\s{1}|^)([\w-]+)', line)
        if result is not None:
            profiles.append(result.group(2))
    return profiles


if os.geteuid() != 0:
    print('must be run as root')
    sys.exit(1)

DEFAULT_PREFIX = 'swift-runway-'
parser = argparse.ArgumentParser()
parser.add_argument('-a', '--all', action='store_true', default=False,
                    help="Delete everything")

parser.add_argument('-p', '--prefix', default=DEFAULT_PREFIX,
                    help="Prefix to look for when deleting. Default: "
                         "'{}'".format(DEFAULT_PREFIX))

args = parser.parse_args()

delete_everything = args.all
prefix = args.prefix

VOLUME_GROUP = 'swift-runway-vg01'

list_command = 'lxc list --format=json'
p = subprocess.run(shlex.split(list_command), stdout=subprocess.PIPE)

containers = json.loads(p.stdout.decode())
to_delete = [x['name'] for x in containers if x['name'].startswith(prefix)]

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
    num_deleted = 0
    for logical_volume in lvlist:
        delete_command = 'lvremove --yes /dev/%s/%s' % (VOLUME_GROUP, logical_volume)
        try:
            p = subprocess.run(
                shlex.split(delete_command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                check=True)
        except subprocess.CalledProcessError as err:
            print('Error deleting /dev/%s/%s:\n%s' % (VOLUME_GROUP,
                                                      logical_volume,
                                                      err.stderr.rstrip()),
                  file=sys.stderr)
        else:
            num_deleted += 1
    else:
        print('%d volumes deleted' % num_deleted)

# delete associated lxc profiles
profile_list_command = 'lxc profile list'
p = subprocess.run(shlex.split(profile_list_command), stdout=subprocess.PIPE)
profiles = parse_profiles_list(p.stdout.decode())
to_delete = [x for x in profiles if x.startswith(prefix)]
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
