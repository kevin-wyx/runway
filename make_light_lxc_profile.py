#!/usr/bin/env python3

import subprocess
import shlex
import sys
import os.path


CNAME = sys.argv[1]
VOLUME_GROUP = sys.argv[2]
try:
    DRIVE_SIZE = sys.argv[3]
except IndexError:
    DRIVE_SIZE = '10G'

dev_numbers = {}


path_to_repo = os.path.dirname(os.path.realpath(__file__))

diskfile = '/tmp/%s-disk' % CNAME

truncate_command = 'truncate --size=%s %s' % (DRIVE_SIZE, diskfile)
p = subprocess.run(shlex.split(truncate_command), stdout=subprocess.PIPE)

#TODO: mount diskfile, put xfs on it, add that as the bind mount to the guest

template_vars = {}
template_vars['host_tmpfs_mount'] = mountpoint

template_file = path_to_repo + '/container_base/swift-runway-ram-v1.tmpl'
raw = open(template_file).read()
formatted = raw.format(name="%s-profile" % CNAME, **template_vars)
print(formatted)
