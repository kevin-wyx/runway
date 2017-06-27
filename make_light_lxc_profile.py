#!/usr/bin/env python3

import subprocess
import shlex
import sys
import os.path

'''
create a rofile for a lightweight guest. This will be used for test targets
which will only have a single `-replica policy. This profile sets up one drive,
meaning that the drive set up here is the total space that can be used for
storage in the test target. Since we're setting it up in /tmp (ie tmpfs),
there is no persistence but also no extra drive space required. The only
storage is RAM.
'''

CNAME = sys.argv[1]
VOLUME_GROUP = sys.argv[2]  # unused
try:
    DRIVE_SIZE = sys.argv[3]
except IndexError:
    DRIVE_SIZE = '1G'

path_to_repo = os.path.dirname(os.path.realpath(__file__))

# put it in /tmp so it's only in the host's memory, not disk
diskfile = '/tmp/%s-disk' % CNAME

truncate_command = 'truncate --size=%s %s' % (DRIVE_SIZE, diskfile)
p = subprocess.run(shlex.split(truncate_command), stdout=subprocess.PIPE)

make_fs_command = 'mkfs.xfs %s' % diskfile
p = subprocess.run(shlex.split(make_fs_command), stdout=subprocess.PIPE)

template_vars = {}
template_vars['host_tmpfs_mount'] = diskfile

template_file = path_to_repo + '/container_base/swift-runway-ram-v1.tmpl'
raw = open(template_file).read()
formatted = raw.format(name="%s-profile" % CNAME, **template_vars)
print(formatted)
